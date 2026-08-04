# S16 — The "calibrated negative" is retracted: the control was measuring its own root

Branch `claude/stable-ac-conjecture-stabilization-rwo9as`. **This branch must be merged into
`fable/proof` by the user** — a cloud session can only push to its own `claude/*` branch, so
nothing here reaches `fable/proof` on its own. No PR opened (`FRAMING` trap 10).

STATUS: **RETRACTION of `S13_SYNTHESIS.md` §3z-bis, plus the instrument fact that replaces
it.** The retracted claim was labelled "THE CALIBRATED NEGATIVE — the strongest result of
the session". It is not a result. What replaces it is smaller, but it is real, and it is
more useful: it says why the search program could never have worked on AK(3).

---

## 1. What §3z-bis claimed

> A matched AC-trivial thickenable control yields **759/50,320 (1.51%)** thickenable states
> at ranks 12–13; AK(3) yields **0/45,111** (expected ≈ 681). So the region is not
> structurally `γ_N ≥ 1` — AK(3)'s zero is a fact about AK(3).

The reasoning: if AC-trivial length-13 rank-2 presentations generically produce thickenable
descendants under the cubic split search, and AK(3) produces none, the difference is about
AK(3).

## 2. The test that kills it

The control family was **widened** from one source to five, all AC-trivial, all rank 2, all
of **total length 13** — the same length band, so no length confound this time
(`experiments/lessons/contrast-length-confound.md`). Same code, same pool builder, same
decider, same `deep_cap = 400000`.

Measured with the repo's own decider on the pool artifacts directly, not from an
end-of-run summary:

| source | words | γ_N of the **source** | decided | `γ_N = 0` hits | rate |
|---|---|---|---|---|---|
| original control `src0` | `('XYXXY','XXYXYXXY')` | **0 — SPHERICAL** | 50,320 | **759** | 1.51% |
| ctrl2 `src0` | `('XyyXy','YxYYYxxY')` | ≥ 1 — NOT_SPHERICAL | 19,132 | **0** | 0 |
| ctrl2 `src1` | `('yXYxx','YxxyXYxx')` | ≥ 1 — NOT_SPHERICAL | 12,012 | **0** | 0 |
| ctrl2 `src2` | `('XYYXYYXY','yxxyy')` | ≥ 1 — NOT_SPHERICAL | 15,154 | **0** | 0 |
| **AK(3)** | `('xyxYXY','xxxYYYY')` | **2** — NOT_SPHERICAL | 45,111 | **0** | 0 |

(ctrl2 `src3`, `src4` are also NOT_SPHERICAL; their rows were not reached inside the 380 s
decide budget and a full-pool rerun is in flight. They cannot change the conclusion — three
independent non-thickenable sources at 0/46,298 already establish it.)

Source `γ_N` values were recomputed here, in this clone, with
`experiments/stable_ac/fable/s12_hunt.decide(words, 400000)`. The one source that yields
hits is the one source that is *already thickenable*. Every source that is not thickenable
yields nothing — **and AK(3) is simply one of them.**

## 3. Therefore

**The 1.51% was not a property of "being AC-trivial". It was a property of that one root
being `SPHERICAL`.** The between-source variance inside the control family — 1.51% versus
three independent zeros — completely swamps the target-versus-control gap that §3z-bis was
reading. AK(3) behaves exactly like every other non-thickenable length-13 AC-trivial source
tested. Its zero is **not** a fact about AK(3).

The "expected ≈ 681" figure is void with the rate that generated it. It was in any case a
number that class members — drawn from a move tree, not independently — could not support
(same lesson file).

**§3z-bis is retracted in full.** Nothing in the session's data distinguishes AK(3) from a
generic non-thickenable balanced trivial-group presentation.

## 3b. The direct evidence: replay the 759 hits' own chains

The aggregate argument of §3 is confirmed at chain level, which is stronger. A6 replayed
every one of the 759 control hits from its root and recorded the defect along the chain:

```
distinct defect sequences (root → … → hit) over all 759 hits:
        (0, 0, 0, 0)  ×  759          ← every single one
chains that left 0 and came back (a SPLIT that CREATED γ_N = 0):   0
```

Not one hit was created. All 759 were `γ_N = 0` at the root and stayed there. So 1.51 % is
the rate at which the pipeline **fails to destroy** a certificate it was handed — and the
"expected ≈ 681" arithmetic silently assumed the pipeline *creates* at the rate it
*preserves*. AK(3) has nothing to inherit: every one of its chord triangulations is
`γ_N = 2` exactly.

**A related fact worth recording:** over 33 random AC-trivial rank-2 presentations of total
length 13, the defect distribution was `{0: 20, 2: 13}` — **defect 4 never appeared**. AK(3)
sits at a defect that is rare for its length, which is why an exactly-matched control could
not be constructed; the sharp controls are at defect 2. They still require creation, and
they still score zero.

## 4. What replaces it — the instrument fact, which is worth more

Four independent measurements, three ranks, one conclusion:

| measurement | rank | creations | opportunities |
|---|---|---|---|
| sharp control (3 non-thickenable sources) | 12/13 | **0** | 46,298 |
| AK(3) pool | 12/13 | **0** | 45,111 |
| **total, decided states from non-thickenable roots** | | **0** | **91,409** |
| flip census (separate experiment) | 5 | **0** | 1,470 |

> The chord + SPLIT pipeline is certificate-**preserving** and certificate-**non-creating**
> — 0 creations in **91,409** decided states from four non-thickenable roots, plus 0 in
> 1,470 rank-5 flip-census opportunities — while the instrument is demonstrably not
> blind: it exhibited 759 certificates, one verified six ways, whenever the root already
> had one.

**A correction to an earlier draft of this table** (caught by the S13 audit, A15): the 759
replayed control chains were originally pooled into this total, giving 93,638. That was
wrong — those chains **start** at defect 0, so they are not opportunities to *create*
anything. They belong in §3b as evidence of inheritance, not here as denominators. The
denominator for a creation rate may only count states descended from a root with
`γ_N > 0`. Note also that these states come from a move tree and are **not** independent
draws, so no p-value may be quoted from them
(`experiments/lessons/contrast-length-confound.md`).

In this move set and search regime, **thickenability is inherited, not generated.** It can
therefore only settle a presentation whose rank-2 root is already thickenable.

**Stated at the strength the evidence actually supports** (the audit caught two overstatements
here): AK(3)'s own rank-2 spelling has `γ_N = 2` by exact census over 86,400 rotations, and no
thickenable member of its class has been found in the 124,296-member rank-2 matched harvest or
the 171,842-member depth-1 stable class — those are **bounded nulls, not an absence proof**,
and their class-wide negation would *be* the disproof. So: **on the evidence, the cubic route
did not settle AK(3)** — the pipeline lowered `γ_N` (527 measured descents 4 → 2, plus `C1` at
`γ_N = 1`) but never reached 0 in 91,409 decided states. That is a **measured instrument
limitation, not a proved obstruction**; no monotonicity theorem forbids reaching 0 (`S15` §6).
Its 0/45,111 says nothing about AK(3) beyond its rank-2 defect.

This retires the route's certificate half **with a mechanism rather than with silence** — the
second publishable outcome `S4` §7.3 named. What survives untouched is the rank-13 cubic form
itself: a normal-form result that never depended on `γ_N`.

The mechanism is exactly what the proved structure predicts. That is
exactly what the proved structure predicts: S3 shows a chord refinement is a *CW
subdivision* that preserves the entire defect histogram by a dart-level bijection, so it
cannot change `γ_N` at all; T4/T4′ show stabilization and the first slide over a fresh
stabilizer are inert. The one move known to lower `γ_N` is A6's length-3 SPLIT
(`AK(3)` at `γ_N = 2` → `C1` at `γ_N = 1`, `S4B`), and in 91,409 states it never carried
anything to 0.

**The design consequence, stated plainly: pointing this search at AK(3) was never going to
produce a certificate.** A program whose moves essentially preserve `γ_N` cannot certify a
root with `γ_N > 0`; it can only confirm roots that were already done. The control did not
validate the instrument for the job — it demonstrated the instrument doing the *only* thing
it can do.

## 5. Bound direction, restated because this is where it bit

Per `S15_ONE_SIDEDNESS.md` §4, every instrument here bounds `Γ(P) = min{γ_N(Q) : Q ~_st P}`
from **above**. The retracted claim tried to turn a null into a statement about AK(3) — a
lower-bound reading of an upper-bound tool. That is the repo's most expensive recurring
trap (`experiments/lessons/parallel-runs-and-bound-direction.md`), and the calibration
control did not protect against it, because the control was calibrating the wrong thing: it
measured *whether hits are findable when the root already has one*, not *whether the search
can manufacture one*.

The correct calibration question for a one-sided search is **"has this instrument ever
produced the thing it is looking for, starting from a state that did not already have
it?"** For this instrument the answer is no, 0 for 91,409.

## 6. Status of every claim in this file

| # | claim | status |
|---|---|---|
| §2 table, source `γ_N` column | recomputed in this clone with the repo decider | **measured** |
| §2 table, hit counts | read from `s4b_control_decided_summary.json` and from `s4b_ctrl2_decided.jsonl.gz` row by row | **measured** |
| §3 retraction of §3z-bis | follows from §2 | **established** |
| §4 "inherited, not generated" | 0 creations in 91,409 decided states from 4 non-thickenable roots | **measured**; it is an instrument fact about this move set and budget, **not** a theorem that `γ_N = 0` is unreachable |
| §4 "S3/T4/T4′ predict it" | those results are proved (S3 audited; T4/T4′ unaudited) | **proved elsewhere**, cited |

Nothing here is a proof or disproof of the AC or stable AC conjecture. §4 in particular must
not be read as an obstruction: it bounds nothing from below, it only says this instrument
cannot supply the certificate.
