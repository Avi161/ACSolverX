# Most of the CoV family is just an automorphism — and the automorphisms are what's winning

## The short version

87.4% of the CoV sweep is the input presentation wearing a different alphabet — a pure relabel, no new coordinates. That was the worry, and it is real. But the follow-up question ("were the fast starts the real ones or the renames?") came back the opposite way from what the worry implies: at budget 100 over the 66-row benchmark, **17 presentations flip from unsolved to solved on a CoV start, and 14 of those 17 flips are pure relabels.** The cap-matched control rules out the length-headroom explanation, and the CoV itself costs zero search nodes.

So a rename is not a no-op for this search. That is the thing to explain before deciding anything about the family.

One correction to carry into the reading: the *path-length* half of the original worry does not survive scrutiny — a CoV row's reported path excludes the transformation's own moves, so it was never a fair proof-length comparison (see † below). The *nodes* half and the flips are real.

## How we tell a relabel from a real change

Every sweep row carries `aut_canon_orig` and `aut_canon_cov` — the Aut(F₂)-orbit canonical representatives of the input pair and of the pair the greedy actually searched from. Two pairs sit in the same orbit **iff** their reps are equal:

- `aut_canon_cov == aut_canon_orig` → **relabel**. Some automorphism of F₂ carries the input to the output. The CoV renamed the coordinates and nothing else.
- `aut_canon_cov != aut_canon_orig` → **moved**. A genuinely different presentation, not reachable from the input by any change of variables.

This is the only sound test. `n_subs` (how many times `w` was swapped for `z`) measures effort, not effect. `iso_index`, `z_word` and the length fields say nothing about it either.

Rigor caveat: `aut_canon` truncates at `level_cap = 50000` in principle. `test_aut_canon_cap_does_not_truncate` pins that it does not truncate on this data (0/150 of the longest outputs changed rep at 400k). If that test ever fails these fields become cap-dependent approximations and the split has to move to an analysis pass.

## Census: 87% of the family is a rename

Across the whole 66-row benchmark, 6722 CoV rows:

|             | `n_subs = 1` | `n_subs ≥ 2` | total |
|-------------|-------------:|-------------:|------:|
| **relabel** |         5867 |            8 |  5875 |
| **moved**   |            0 |          847 |   847 |

**5875 of 6722 rows (87.4%) are the input presentation, renamed.** Only 847 (12.6%) are new coordinates. Without these two fields you would read the jsonl as 6722 changes of variables when it contains 847. Distinct `aut_canon_cov` values — how many orbits the family actually touches — is 399 across the benchmark, and only **2** for AK(3) out of its 34 valid CoV starts.

The `n_subs ≥ 2` column also kills `n_subs` as a cheap substitute for the orbit rep: 8 rows did real substitution work, twice over, and landed back in the input's orbit. They look like progress and are not.

## The confound, and how it was controlled

The sweep's built-in control runs the **original** strings at the base cap 24. A CoV row runs the transformed strings at `max(24, longest_transformed + 16)` — median 32, stored per row as `max_relator_length_cap`. So "the CoV beat the control" and "the CoV had more length headroom" are not separated by the sweep alone, and a larger cap can move `nodes_explored` either way (fewer no-op moves = more real successors — sometimes a shortcut, sometimes wider branching).

So every apparent winner got a third search: the **original** strings re-run at the CoV row's own cap `K`. A win counts only if the CoV also beats `control@K`. In the event the cap turned out to be inert on this data — `control@K` equalled `control@24` on every presentation — but that is a measured result, not an assumption, and it has to be re-measured whenever the family's lengths change.

## Result: budget 100, 66 presentations, 6788 rows

Per presentation, taking the best CoV start and comparing against both controls:

| best CoV start by | REAL WIN (beats cap-matched control) | of which **relabel** | of which **moved** |
|---|---:|---:|---:|
| `nodes_explored` | 34 / 66 | **23** | 11 |
| `path_length` † | 34 / 66 | **22** | 12 |

**Unsolved → solved flips** (control unsolved at *both* caps, some CoV start solves within 100 nodes): **17 presentations — 14 from a relabel, 3 from a moved start.**

> † **The path row is not a certificate comparison — do not read it as "CoV finds shorter proofs."** A row's `path_length` counts only the search *after* preprocessing, so a CoV row's path runs from the already-transformed start and excludes the stabilize/substitute/isolate/destabilize moves that got there. The control has no preprocessing, so its `path_length` *is* the full certificate. `PROOFS.tex` §"Claims to avoid" states this directly. The **nodes** axis and the **flips** are unaffected and carry the finding on their own: the CoV is computed analytically at a cost of zero search nodes, so `nodes_explored` is like-for-like, and a flip is solved-vs-unsolved, where the control has no path at all.

Some of the individual jumps are large, and the ones with `n_subs = 1` are pure renames by the proof below:

| pres | control@24 | best CoV | orbit | z | what happened |
|---|---:|---:|---|---|---|
| 331 | 93 nodes | 9 nodes | relabel | `Xyx`, `n_subs=1` | 10× fewer nodes, provably a rename |
| 303 | 70 nodes | 10 nodes | relabel | `xyX`, `n_subs=1` | provably a rename |
| 201 | 61 nodes | 10 nodes | relabel | `Xyx`, `n_subs=1` | provably a rename |
| 247 | 46 nodes | 9 nodes | relabel | `yyyX`, `n_subs=1` | provably a rename, **at the same cap 24** |
| 579 | UNSOLVED | 11 nodes | relabel | — | flip |
| 288 | UNSOLVED | 12 nodes | relabel | — | flip |
| 0 | 3 nodes | 2 nodes | relabel | `Yxy`, `n_subs=1` | provably a rename |

### Worked example: 331, with the automorphism written out

This is the one to look at, because `n_subs = 1` puts it squarely inside the proof below — it is not "empirically in the same orbit", it is a rename by construction.

```
pres 331    z = Xyx    isolate x from r2′    n_subs = 1
input     <x,y | YYYYXyyyx     , YYXYxYx  >     93 nodes,  cap 24
CoV       <x,y | XXXXXXYxxxyxx , YXXYxyxx >      9 nodes,  cap 29
aut_canon(input) = aut_canon(CoV) = ( YYXXYx , YYYYXyyyx )      identical
```

The CoV's own steps *are* the automorphism, read end to end. Name `z = Xyx`; it occurs exactly once, in `r2`, so `YYXYxYx → YYZYx` and `r1` is untouched. Solve that isolator for `x`: `YYZYx = 1` gives `x = yzyy`. Destabilize and relabel the survivors `(y, z)` back to `(x, y)` — so old `y` becomes new `x`, and `z` becomes new `y`. Pushing `x = yzyy` through that relabel gives:

```
φ :  x ⟼ xyxx          φ⁻¹ :  x ⟼ y
     y ⟼ x                    y ⟼ YxYY
```

φ is an automorphism because `{x, xyxx}` is again a free basis of F₂ — `y` is recoverable as `X·(xyxx)·X·X = y`, so both generators lie in the image and φ is onto (hence bijective on a free group of finite rank). Verified: `φ∘φ⁻¹ = φ⁻¹∘φ = id` on both generators. And it carries the input to the output on the nose:

```
φ( YYYYXyyyx )  =  XXXXXXYxxxyxx                              exactly the CoV's r1
φ( YYXYxYx   )  =  XXXXYXyxxyxx  =  YXXYxyxx                  after cyclic reduction + rotation
```

So the whole "change of variables" here is: **rename `y` to `x`, and rename `Xyx` to `y`.** Same group, same problem, zero AC work. The relators look unrecognizable (9 letters vs 13) only because a change of basis is free to lengthen words — which is exactly why eyeballing the strings, `n_subs`, or the length fields cannot tell you a rename from a real move, and `aut_canon` can. This is the general proof below instantiated at `m = 2, n = 1, η = −1, ε = +1`.

### Worked example: 247, the confound-free one

331 ran at cap 29 against a control at cap 24, so it needs the cap-matched control to be believed (it survives it — `control@29` is also 93). 247 needs nothing at all:

```
pres 247    z = yyyX    isolate x from r1′    n_subs = 1
input     <x,y | YYYXyyx , YYXyyXyx >    46 nodes,  cap 24
CoV       <x,y | XXyyxY  , YxxxyXX  >     9 nodes,  cap 24     ← identical cap
aut_canon(input) = aut_canon(CoV) = ( YYXXyx , YXXXyxx )       identical
```

Same cap, same orbit, provably a rename, **46 nodes → 9**. There is no headroom difference to argue about and no length story to tell: the only thing that changed is which letters the presentation is written in.

### Per-row the picture inverts, and both halves matter

Among all CoV starts that solved, checked against their own cap-matched control:

| | beats cap-matched control | does not |
|---|---:|---:|
| **relabel** | 478 | 412 |
| **moved** | 109 | 60 |

Solve rate at budget 100: **relabel 890/5875 = 15.1%**, **moved 169/847 = 20.0%**. So an individual *moved* start is about 1.3× likelier to help — moved rows are 12.6% of the family but 16.0% of the solved starts, genuinely enriched. Relabels nonetheless supply **84% of all solved starts** and 14 of the 17 flips, purely because there are seven times more of them.

Both readings are true and they answer different questions. *Which kind of CoV is better per attempt?* Moved. *Which kind is actually producing the results in this sweep?* Relabels, by volume. Neither fact licenses dropping the other kind.

## Why a rename can possibly help at all

The greedy operates on **strings**, not on orbits. Nothing in it is Aut(F₂)-invariant: the move ordering, the priority tie-breaks, the cyclic-reduction normal form and the per-relator cap all read the literal letters. So two presentations in the same orbit are the same *problem* but not the same *search*, and `PROOFS.tex` says so explicitly in its "claims to avoid" — *"No boundary CoV can improve greedy nodes." False as a universal search claim: labels, tie-breaking, preprocessing, and the per-row cap can alter bounded exploration.*

What is new here is the magnitude. "Tie-breaking noise" does not turn 93 nodes into 9, and it does not flip 14 presentations from unsolved to solved. That is a systematic effect, and the honest description right now is that **we do not know what makes a good relabel good.** The relabel family is behaving like a cheap restart-with-a-different-representation, and its 15.1% hit rate is doing real work at a budget where the control gets nothing.

## Is every `n_subs = 1` CoV an automorphism?

Yes for the shipped subwords family, and it is **provable for any `|w|`** — including `z = xx` and other pure powers. This is a strengthening of what `PROOFS.tex` currently contains, so the attribution matters:

**What PROOFS.tex actually proves.** Corollary *"Only-occurrence degeneracy"* is a corollary of the *Exact relator-minus-one factorization* theorem, whose hypothesis 1 is `R = w^η a^ε` — the **two-letter isolator**, i.e. `|w| = |R| − 1` exactly. The paper's own §"Claims to avoid" says it: *"The proof applies only to the stated two-letter isolator."* And the shipped no-collapse gate (`MIN_TRANSFORMED_LEN = 3`) **rejects exactly those `w`**, because they collapse `R` to length 2. So **no shipped row is inside that corollary's scope** — measured over relator words of length 2..5, all 544326 `n_subs = 1` rows sit at `|R| − 1 − |w| ≥ 1` (441606 at gap 1, 102720 at gap 2), **none at gap 0**. Citing the corollary for these rows would be citing a theorem whose hypothesis the data never meets.

**The general proof.** Let the single selected occurrence sit in `R`, so the other relator `S` has none and `S_z = S`. Then:

1. `R_z` is forced to be the isolator — `S` has no `z`, and defining-relator isolation is off in this family.
2. Isolation needs exactly one `a^{±1}` in `R_z`. Since `R_z = z^η t` with `t` a word in `a, b` carrying that single `a`, `t` is pure `b`-powers around it: `t = b^m a^ε b^n`. Hence `R = w^η b^m a^ε b^n`.
3. Rotating `R_z = z^η b^m a^ε b^n` to put `a` first gives `a^ε · b^n z^η b^m = 1`, so `a = (b^n z^η b^m)^{−ε} =: α`.
4. **`ψ : a ↦ α, b ↦ b` is an isomorphism `F(a,b) → F(b,z)`** — its inverse is `z ↦ (b^{−n} a^{−ε} b^{−m})^η`, and `χψ(a) = ((a^{−ε})^{−ε}) = a`. This holds for **any** `|w|`; nothing here needs `|w| = |R| − 1`.
5. The kept relators are `ψ(S)` (since `S_z = S`) and `z^{−1}ψ(w)` (the defining relator `Zw` with `a` eliminated). And `ψ(R) = ψ(w)^η · α^ε`-sandwiched `= ψ(w)^η z^{−η}` — which is a **rotation** of `z^{−1}ψ(w)` when `η = +1` and its **inverse** when `η = −1`.

So the output is `{ψ(R), ψ(S)}` up to relator order, rotation and inversion, with `ψ` an isomorphism — an automorphism of F₂ after the relabel. The output *is* the input, renamed. ∎

**Verified computationally, mechanism and not just conclusion.** The identity `output == {ψ(R), ψ(S)}` (up to order/rotation/inversion) holds on **544326 / 544326** `n_subs = 1` rows over all relator words of length 2..5, every one outside the published corollary's scope and 102720 of them two letters clear of its hypothesis. Separately, `aut_canon` confirms the conclusion on the length-2..4 slice: **0 / 18460** left the orbit, and **0 / 4700** of the pure-power-`z` rows (`z = xx`, `yy`, …) left it either.

**Scope — where the proof stops.** Step 1 is the load-bearing hypothesis. In the **universe** family the defining relator `Zw` is a legal isolator (`iso_index = 2`), `z` need not occur in the presentation at all, and the argument above does not reach it. Empirically the conclusion still holds there — 61207 `n_subs = 1` rows with `Zw` isolation allowed, **0 moved** — but that is measurement, not proof. (It is very likely provable by a similar argument: isolating `a` from `Zw` requires `w = b^m a^ε b^n`, which makes `{b, w}` a Nielsen basis outright.) Do not state "any `n_subs = 1` CoV is an automorphism" without the subwords-family qualifier.

## What is not decided here

Nothing — this is the evidence, not a recommendation.

The tempting conclusion is "87% of the family is a rename, so drop the relabels and keep the 847." The data says that would delete 14 of the 17 unsolved→solved flips. The opposite conclusion, "relabels are what works," ignores that per attempt a moved start is the better bet.

The real open question is the one in the middle: **what distinguishes a relabel that turns 93 nodes into 9 from the 85% that do nothing?** If that is answerable, it is worth more than the CoV family itself — it would be a statement about what representation this greedy is sensitive to, which applies to every presentation, not just the ones a CoV happens to reach. If it is not answerable, the relabel family is still a working cheap-restart mechanism at a 15% hit rate, and should be judged as one rather than as mathematics.

Also unresolved: the 12 primitive-output rows that leak past the no-collapse gate (tag or drop), and whether any of this survives at production budgets — everything above is budget 100, where the control solves only 47/66.

## Reproducing

```bash
# the sweep (66 presentations x every CoV start + control, budget 100)
.venv/bin/python3 -m experiments.stable_ac.cov.run_cov --config <cfg> --budget 100 --experiment-length --high-speedup
# -> results/stable_ac/cov/covsweep_100_66_subnc2pxysb_mrl24_cyc_s60r6_<date>.jsonl
```

Analysis scripts (orbit split with cap-matched controls; the `n_subs=1` proof check) are scratch, not shipped — the census and the win split are both a groupby on `aut_canon_orig == aut_canon_cov` plus one re-run of the original strings at each winner's `max_relator_length_cap`.
