# S21 — The matched calibrated negative: AK(3) 0/34 against 35/40

Branch `claude/stable-ac-conjecture-stabilization-rwo9as`. **This branch must be merged into
`fable/proof` by the user** — a cloud session can only push to its own `claude/*` branch, so
nothing here reaches `fable/proof` on its own. No PR opened (`FRAMING` trap 10).

STATUS: ~~the session's strongest negative measurement~~ — **HEADLINE RETRACTED WITHIN THE
HOUR. The control design failed for a FOURTH reason, and this one is the deepest.**

> ## ⛔ THE 35/40 IS NOT A COMPARABLE RATE — see §0 below and `S18_S5_RECHECK.md`
>
> **The controls escape through a region AK(3) provably cannot enter.** Every control hit is
> a walk *down* in length: the witness lengths are 3, 3, 4, 4, 4, 5, 7, 7, 8, 9, 9, 9, 9, 10,
> 11, 11, 11, … against a starting length of 13. But **any member of AK(3)'s class below
> length 13 would settle the open problem outright** (Havas–Ramsay exhausted that region), so
> AK(3) cannot use the exit that produced essentially every control hit.
>
> Restricting to the three targets at AK(3)'s own length 13, and requiring only the weak
> condition that the *witness itself* be back in band (`length ≥ 13`):
>
> | | trials | hits | rate |
> |---|---|---|---|
> | raw, as reported in §4 | 24 | 19 | 0.79 |
> | **witness length ≥ 13** | 24 | **8** | **0.33** |
>
> And 0.33 is still an over-estimate, for two reasons. The witness being back in band does
> not mean the *chain* stayed in band — it may dip and return. And total length is inflatable
> by inert AC4 discs, so a long witness can be a short core in disguise: A18 applied the core
> test to the S5 ladder's 39 witnesses and **39 of 39** reduced to a rank-2 core of length 8
> or 11, with only **2** surviving an AC-legal-only reduction.
>
> The decisive datum is A18's, on a freshly built defect-matched control (`γ_N = 2`,
> AC-trivial, length 13): **8/40 hits, all genuinely created (`4→2→0`), and 0 of the 8 stay
> in band** — minimum chain lengths 5, 7, 7, 9, 9, 11, 11, 11. Also **0/32 at rank ceilings
> 3–6**: extra rank actively *hurt* at fixed budget.
>
> **Therefore AK(3)'s 0/34 is consistent with the matched control's in-band rate, which may
> well be 0.** §6's reachability claim does not survive, and the "leans toward the disproof
> side" remark in §6 is withdrawn outright.
>
> **What survives:** §3 (stabilization is inert for `γ_N`, exact census at ranks 2–5 — an
> independent result that never depended on the comparison); the observation that matched
> defect-4 controls exist at all; and the negative lesson itself, filed as **T-S20**.

It is a *measurement*, not a theorem, and it bounds `Γ(AK(3))` from **above** only. It is not
a proof that AK(3) lacks a thickenable member.

## 0. Why this failed, and why it is a different failure from the first three

This comparison has now failed four times, each time because the control was unmatched on a
variable that only became visible after the result was read:

| # | the control was matched on | the variable that broke it |
|---|---|---|
| 1 | AC-triviality, rank, length | it was **already `γ_N = 0`** — survival, not creation (T-S19) |
| 2 | + verified non-thickenable | it sat at **defect 2**, a one-unit descent; AK(3) needs two |
| 3 | + **defect 4**, a two-unit descent | it can **exit the length band**; AK(3) cannot (**T-S20**, this file) |

The fourth costume is the deepest because the escape is closed to the target *by the very
openness of the problem*: AK(3) cannot reach length ≤ 12 precisely because reaching it would
be a solution. Any control that is known AC-trivial can walk down; the target cannot be
allowed to, or there would be nothing to measure. **This is not a fixable control design —
it is a structural limit on target-versus-control comparisons for this problem**, and it
subsumes the §5.2 caveat, which said the same thing less sharply and was not acted on.

---

## 1. Why the earlier versions of this comparison failed

This is the third design. The first two are retracted, and the reason each failed is the
reason this one is built the way it is.

| attempt | control | why it failed |
|---|---|---|
| §3z-bis (retracted, `S16`) | AC-trivial, rank- and length-matched | it was **already `γ_N = 0`**, so its 759 hits were *survivals*, chain `(0,0,0,0)` × 759 — it measured a rate the target could not be compared against (trap **T-S19**) |
| the `s12` hunt at length 13 | AC-trivial, length-matched, verified **not** thickenable | matched on thickenability but sat at **defect 2**, i.e. a **one**-unit descent, while AK(3) sits at **defect 4** and needs **two**. Same trap, third costume: matched on every axis except the one that matters |
| **this one (S21)** | AC-trivial, length-matched, **defect 4** | matched on the descent depth as well — see §2 |

The defect-4 controls were found *before* the comparison was read, not in autopsy. An
earlier agent had reported defect 4 never appearing in 33 random AC-trivial length-13
presentations, so the natural conclusion was that no matched control exists. Scanning
harder — 240 solved-ladder members, lengths 11–18, reading the defect off the **stabilized**
form (legitimate because stabilization is machine-confirmed inert for `γ_N`, §3) — found
**78** with a defect number: 73 at defect 2 and **five at defect 4**.

## 2. The design

Every axis the instrument sees is matched:

| axis | AK(3) | the five controls |
|---|---|---|
| group | trivial | trivial |
| rank | 2 | 2 |
| total length | 13 | 13 (three of them), 12 (two) |
| `minimum_defect` / `γ_N` | **4 / 2** | **4 / 2** |
| descent required to reach `γ_N = 0` | two units | two units |
| instrument | `s12_hunt`, 8,000 nodes, headroom 4, depth 0 | identical |

The controls are AC-trivial solved Miller–Schupp instances; AK(3) is a balanced presentation
of the trivial group whose AC status is open. That last difference is the one axis that
cannot be matched, and §4 treats it as the load-bearing caveat it is.

## 3. Supporting fact, machine-confirmed here: stabilization is inert for `γ_N`

| presentation | rank 2 | rank 3 | rank 4 | rank 5 |
|---|---|---|---|---|
| AK(3) | NOT_SPHERICAL | defect **4** | defect **4** | defect **4** |
| control `('YYYXyxyX','YYXyx')` | NOT_SPHERICAL | defect **2** | defect **2** | defect **2** |
| control `('YYYXyyxx','YYXyx')` | NOT_SPHERICAL | defect **2** | defect **2** | defect **2** |

Exact census, this clone. This is a machine confirmation of **T4** (AC4/AC5 wedge on a
2-disc) and it carries two consequences:

* **A direct answer to the session brief.** *Adding generators alone does not move `γ_N` at
  all, at any rank.* AK(3) is still at `γ_N = 2` at rank 5, and would be at rank 20. A hard
  presentation does not become easier by being stabilized; only moves that **use** the new
  generators can help, which is why A6's length-3 SPLIT (`γ_N` 2 → 1) was the single
  mechanism this session found that ever moved it.
* **The calibration carries to every depth.** A control verified non-thickenable at rank 2
  stays non-thickenable however deep it is stabilized, so it remains a valid *creation*
  control at every rung of a depth ladder.

## 4. The result

**Matched defect-4 AC-trivial controls, `s12_hunt` at 8,000 nodes, depth 0:**

| control | length | trials | hits | rate |
|---|---|---|---|---|
| `('YYXyx','YYxxxyXX')` | 13 | 8 | 7 | 0.88 |
| `('YYXyx','YYxxyXXX')` | 13 | 8 | 4 | 0.50 |
| `('YYXyx','YXYXXyxx')` | 13 | 8 | 8 | 1.00 |
| `('YYXyx','YXXYxxx')` | 12 | 8 | 8 | 1.00 |
| `('YYXyx','YXXXYxx')` | 12 | 8 | 8 | 1.00 |
| **pooled** | | **40** | **35** | **0.875** |
| *length-13 only (exact match)* | 13 | 24 | 19 | *0.79* |

**AK(3), same instrument, same budget, depth 0, three independent runs with different
seeds:**

| run | nodes | trials | hits |
|---|---|---|---|
| `s12_ak3_hi_k0` | 8,000 | 16 | **0** |
| `s12_ak3_hi_k1` (its depth-0 row) | 8,000 | 12 | **0** |
| `s12_ak3_depth_ladder` (its depth-0 row) | 2,000 | 6 | **0** |
| **pooled** | | **34** | **0** |

Each of those runs carried its own non-thickenable controls, which scored 15/16, 12/12 and
9/9 respectively — so the instrument was working in every run that produced a zero.

> **A search that creates a thickenability certificate in 35 of 40 attempts on presentations
> matched to AK(3) on group, rank, length and defect creates none for AK(3) in 34 attempts.**

## 5. What this does NOT establish — the four caveats, in order of importance

1. **Bound direction.** This bounds `Γ(AK(3)) = min{γ_N(Q) : Q ~_st AK(3)}` from **ABOVE**
   only, and it failed to move it. It is **not** evidence that `Γ(AK(3)) ≥ 1`. Per `S15` §4
   the whole thickenability route is one-sided: Lackenby's Thm 1.3 is an implication, so a
   *hit* would settle AK(3) positively and a *miss* settles nothing. This result must never
   be summarised as "AK(3) has no thickenable member" — that statement is the disproof of the
   stable AC conjecture and nothing here comes close to it.
2. **AC-distance is unmatched, and cannot be matched.** The controls are *known* AC-trivial
   with short witnesses; AK(3)'s AC-distance to the trivial presentation is precisely the
   open question. A control's fast hit may therefore reflect its proximity to triviality
   rather than its defect. **No choice of control removes this** — any presentation known to
   be AC-trivial is by definition close in a way AK(3) is not known to be. This is the
   irreducible limit of the entire target-versus-control method on this problem, and it
   should be stated every time the method is used.
3. **The five controls are not five independent presentations.** All five share the first
   relator `YYXyx` and come from the same solved-ladder family. The effective number of
   independent controls is smaller than five — possibly much smaller. The pooled 0.875 should
   be read as "this family creates readily", not as a population rate.
4. **No p-value, and none is computable.** The 40 control trials are independent randomized
   restarts, but the per-trial success probability is **target-specific**, so the control's
   rate is not AK(3)'s null hypothesis. Quoting `0.125^34` or anything like it would be
   meaningless. (Separately, states within a class come from a move tree and are not
   independent draws — `experiments/lessons/contrast-length-confound.md`.)

Two smaller limits: this is **depth 0 and depth 1 only** — the depth ladder past depth 1 is
still running — and it is one move set (`s12_hunt`'s slides), not all AC moves.

## 6. What it is worth

Given the caveats, the honest positive statement is about **reachability**, and it is this:

> From AK(3)'s rank-2 spelling, a thickenable member of its stable class is not reachable by
> this instrument within 8,000 nodes at depth 0 — while from AC-trivial presentations matched
> on group, rank, length and defect, one is reachable in 35 of 40 attempts.

That is the strongest calibrated statement this line has produced, and it is the first one
whose control survives all three versions of the survival-versus-creation trap. It leans, as
weak evidence only, toward the **disproof** side: by `S15` §5a (unconditional) every stably
AC-trivial presentation *does* have a thickenable member in its class, and this instrument
finds such members readily for matched controls. But a bounded search that finds nothing is
evidence about the search, and this one has now been wrong twice about exactly that.

## 7. Status of every claim

| # | claim | status |
|---|---|---|
| §2 defect match | source defects recomputed in this clone by exact census | **measured** |
| §3 stabilization inert | exact census at ranks 2–5 on three presentations | **measured**; it confirms **T4**, which is *proved* (A8, unaudited) |
| §4 control rates | five runs, artifacts `s12_d4ctl_*.json` | **measured** |
| §4 AK(3) 0/34 | three runs, artifacts `s12_ak3_hi_k0.json`, `s12_ak3_hi_k1.json`, `s12_ak3_depth_ladder.json` | **measured** |
| §5 caveats 1–4 | reasoning about the method | **established** |
| §6 "leans toward disproof" | explicitly labelled **weak evidence**, not a result | **asserted, and flagged as such** |

Nothing in this file is a proof or disproof of the AC or stable AC conjecture.
