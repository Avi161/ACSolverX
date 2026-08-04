# S18 — S5's depth ladder re-audited under T-S19: the control creates, but only by an exit AK(3) does not have

Branch `claude/stable-ac-conjecture-stabilization-rwo9as`. **This branch must be merged into
`fable/proof` by the user** — a cloud session can only push to its own `claude/*` branch. No PR
opened (`FRAMING.md` trap 10). Nothing here is a proof or disproof of AC or stable AC.

TARGET: `S5_RANK_N_SEARCH.md` §4.1 / §5.2 — the depth ladder, **AK(3) 0/40 against a
length-matched control's 39/40**, which `S5` §5.2 calls "the one cell of the whole task where
the null is *not* vacuous".

VERDICT IN ONE LINE: the control root really is non-thickenable and the instrument really does
**create** certificates (39 creations, 39/39 chains verified `2 → … → 0`) — so S5's instrument
is qualitatively stronger than the retracted cubic pipeline of `S16`. But **every one of the
39 certificates rests on a rank-2 core of total length 8 or 11**, i.e. inside the
Havas–Ramsay region AK(3) cannot enter without settling the open problem outright. Once that
exit is controlled for, the surviving creation rate is between **0/40 and 2/40**, and a
freshly built **defect-matched** control (γ_N = 2, length 13, rank 2, AC-trivial) scores
**0/40 in band**. At those rates 40 AK(3) runs are expected to produce **0 to 2** hits.
**0/40 is consistent with the control and carries essentially no information about AK(3).**

New code, this file only: `experiments/stable_ac/fable/s18_s5_chain_audit.py`
(`roots` | `chains` | `cores` | `scan4`). It imports `rank_n_ac_search` and *modifies nothing*;
chains are recovered by wrapping `sample_moves` in a recorder that forwards every argument
untouched, so the replay is bit-identical to the persisted run. New artifacts:
`results/stable_ac/fable/s18_roots.json`, `s18_control_chains.json`, `s18_witness_cores.json`,
`s18_defect4_scan.json`, `s18_defect4_ladder.json`.

Units: `defect` is the UNHALVED Neuwirth defect; **`γ_N = defect // 2`**
(`experiments/lessons/stabilization-that-only-rebookkeeps-is-inert.md`). Every hunted witness
bounds `γ_N` from **ABOVE**; no null below bounds anything from below
(`experiments/lessons/parallel-runs-and-bound-direction.md`).

---

## 1. The control root is genuinely NOT_SPHERICAL — S5 line 190 stands [MEASURED]

Recomputed in this clone, exact census (not the hill-climb, not a summary file):

| root | rank | total length | census enumerated | `minimum_defect` | **γ_N** | verdict |
|---|---|---|---|---|---|---|
| **S5 ladder-D control** `⟨x,y \| YYxxx, YxYxYxxx⟩` | 2 | **13** | 120,960 | **2** | **1** | **NOT_SPHERICAL** |
| **AK(3)** `⟨x,y \| xyxYXY, xxxYYYY⟩` | 2 | **13** | 86,400 | **4** | **2** | NOT_SPHERICAL |
| `S16`'s retracted cubic control `⟨x,y \| XYXXY, XXYXYXXY⟩` | 2 | 13 | 120,960 | 0 | 0 | SPHERICAL |

`s12_hunt.decide(words, 400000)` independently returns `NOT_SPHERICAL / r1c_v2_solver` for the
control root, agreeing with the census. The five ladder-D start states (base stabilized
`k = 0…4`) are **all** defect 2 (`s18_roots.json`), and AK(3)'s five are all defect 4 — an
empirical confirmation of `S6` T4 (AC4 is inert) on exactly the states used.

So the T-S19 failure mode **does not apply here**: this control does not already have the
property. S5's description of it as a "length-matched AC-trivial `NOT_SPHERICAL` AK(2)-class
control" is accurate, and the note in `S5` §3 that the two families are length-matched at 13 is
accurate.

Note what is *not* matched, and it is the second thing T-S19 tells you to put in its own
column: **γ_N(control) = 1, γ_N(AK(3)) = 2.** §5 measures what that costs.

## 2. Were the 39 hits CREATED? Yes — 39 of 39 [MEASURED / RECONSTRUCTED]

All 40 ladder-D control runs were replayed with parent tracking and each hit's chain was
walked back to the root; the defect of **every node of every chain** was then decided
independently (exact census where the family fits under 200,000, else `s12_hunt.decide`).

* **replay fidelity: 40/40** runs reproduce the persisted `hit`, `nodes_used` and `best_state`
  in `rank_n_ac_search_depth_ladder_rows.jsonl` exactly. The reconstruction is not a
  re-simulation, it is the same run.
* **chains reconstructed: 39/39.** None imputed.
* **created: 39. inherited: 0.** Every chain begins at defect 2 and ends at defect 0.

Distinct defect sequences (root → … → witness), the `S16` §3b test applied here:

```
(2, 0)                                          × 20     <- one move from the root
(2, 2, 0)                                       ×  5
(2, 2, 2, 0)                                    ×  7
(2, 2, 2, 0, 0) / (2,2,2,2,0) / 5 longer chains ×  7
chains that started at 0:                          0
```

Compare `S16`: `(0,0,0,0) × 759`, zero creations in 93,638. **This instrument creates.** On the
creation question alone, S5's ladder is the strongest calibration on the S-line.

That is where the good news stops.

## 3. The length confound: S5's own criterion does not survive contact with the witnesses [MEASURED]

S5 §4.1 / §5.2 qualification 2 concedes that part of the control's advantage is its ability to
shrink below length 13, and offers **total length ≥ 13** as the in-band criterion, giving
14 of 39. That count is confirmed — and so is the fact that it measures nothing.

**Total length is not scale-invariant once stabilizers exist.** Adjoining `AC4` discs adds
length without changing the presentation's content (`S6` T4). Concretely, the in-band hit
`depth_ak2ctl_k2_r4` is the witness `⟨x,y,a,b | XyX, YxYxYxxx, a, b⟩`: total length 13, rank 4,
"in band" — and it is the **length-11 rank-2 pair** `⟨x,y | XyX, YxYxYxxx⟩` wedged with two
discs. It was produced from the root by a **single rank-2 AC2 move** `r₁ ← r₁r₂⁻¹`.

Two structural reductions of every witness (`s18_witness_cores.json`):

| reduction | what it is | legality |
|---|---|---|
| `elim` | delete each generator occurring **exactly once** (AC3 + one ambient automorphism fixing all other relators + AC5) | stable-AC legal at rank 2; **[ASSERTED at rank > 2]** — `FRAMING.md` trap 2 records the stable ambient automorphism principle as proved at rank 2 only |
| `tietze` | delete each relator that is a bare generator, striking that generator everywhere | group-legal; **not** an AC move — a structural description only |

| criterion | hits passing | rate over 40 runs |
|---|---|---|
| S5's: chain total length ≥ 13 throughout | 14 | 0.350 |
| `elim` core still has total length ≥ 13 | **2** | **0.050** |
| `tietze` core still has total length ≥ 13 | **0** | **0.000** |

* **39 of 39** witnesses have `tietze` core of **rank 2** and total length **8** (27 of them) or
  **11** (12 of them). Both are below AK(3)'s floor of 13. Every core is itself defect 0.
* **34 of 39** witnesses carry a sub-13 base-generator-only pair *verbatim* among their
  relators (11 of the 14 "in band" ones).
* Only **2** hits survive the `elim` criterion, both rank 3, both at chain length ≥ 13:
  `⟨x,y,b | XybX, bXXXyXyXy, b⟩` (L 14) and `⟨x,y,a | XyXa, YxYxYxxx, a⟩` (L 13). These are
  genuine rank-3 certificates that no AC5 destabilizes — but even their `tietze` cores are the
  length-11 pair, so the mechanism is the same one wearing an extra generator.

**The length-controlled created rate is 2/40 = 0.050 at the most generous honest reading, and
0/40 under the structural one.** S5's 14/39 is an artefact of measuring padded length.

Independent corroboration that the exit is the mechanism, not the rank: the eight `k = 0` hits
are not eight successes. They are **one** witness, `⟨x,y | YYxxx, xYx⟩` (length 8), found by all
eight seeds at node 2 by the identical single move `("ac2", 1, 0, −1)`, i.e. `r₂ ← r₂r₁⁻¹`
dropping the presentation from 13 to 8 letters. Across all 39 hits there are only **25 distinct
witnesses and 2 distinct cores**.

## 4. Rank: S5 §5.2 qualification 3 is misstated, and the corrected version is sharper [MEASURED]

`S5` line 236/392 says *"25 of the 39 control hits are rank-2 or rank-3 thickenable cores"*.
Measured best-rank histogram of the 39 hits:

| best rank | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|
| hits | 10 | 7 | 9 | 9 | 4 |

**17**, not 25, are at best-rank ≤ 3. The 25 is `39 − 14` = the number of witnesses with **no**
entangled stabilizer, a different quantity that S5's prose merged with the rank count. Both
"14"s in S5 §4.1 are also different sets that happen to share a count: entangled ∧ in-band 11,
in-band only 3, entangled only 3, neither 22.

Created **and** length-controlled, by the rank actually used:

| criterion | rank 2 | rank 3 | rank 4 | rank 5 | rank 6 |
|---|---|---|---|---|---|
| S5's ≥ 13 criterion (14 hits), by witness best-rank | **0** | 1 | 3 | 7 | 3 |
| same 14, by `max` rank reached on the chain | 0 | 0 | 3 | 4 | 7 |
| `elim`-surviving (2 hits), by witness best-rank | 0 | 1 | 1 | 0 | 0 |
| `elim`-surviving (2 hits), by `elim`-core rank | 0 | **2** | 0 | 0 | 0 |
| `tietze`-surviving (0 hits) | — | — | — | — | — |

Reading for the session's brief (*does going past 3 generators help?*): **every rank-2 hit is
out of band and every in-band hit uses rank ≥ 3** — but in 12 of the 14 cases the extra rank is
carrying a below-13 rank-2 core, not certifying anything new. Extra generators bought length
padding, not topology. §5 measures the same question on a harder root and gets a *negative*
answer.

## 5. NEW: a defect-matched control — the sharp experiment S5 could not run [MEASURED]

`S16` §3b reported that defect 4 never appeared among 33 random AC-trivial length-13 rank-2
presentations, and concluded no exactly-matched control could be built. **That is too
pessimistic.** Deciding 260 `NOT_SPHERICAL` AK(2)-class members of total length 13 by exact
census (`s18_defect4_scan.json`) gives `{defect 2: 258, defect 4: 2}` — rare, but they exist:

> `⟨x,y | YYYxx, YYXYxyyx⟩` and `⟨x,y | YYYxx, YYXyyxyX⟩`, both length 13, rank 2, AC-trivial
> (members of AK(2)'s AC class, which the battery trivializes in a replay-verified 27 moves),
> both exact `minimum_defect` **4**, i.e. **γ_N = 2 — AK(3)'s own value**.

The identical ladder-D protocol (5 rungs × 8 seeds, 600 nodes) was run on the first of them
(`s18_defect4_ladder.json`):

| ladder root | γ_N | k=0 | k=1 | k=2 | k=3 | k=4 | total | created | **in band** |
|---|---|---|---|---|---|---|---|---|---|
| S5 control `YYxxx, YxYxYxxx` | 1 | 8/8 | 8/8 | 8/8 | 7/8 | 8/8 | **39/40** | 39 | 14 by S5's rule, **2** by `elim`, **0** by `tietze` |
| **defect-matched** `YYYxx, YYXYxyyx` | **2** | **8/8** | 0/8 | 0/8 | 0/8 | 0/8 | **8/40** | 8 | **0/8** |
| AK(3) `xyxYXY, xxxYYYY` | 2 | 0/8 | 0/8 | 0/8 | 0/8 | 0/8 | **0/40** | — | — |

Three things fall out, all measured:

1. **The defect gap is not the barrier.** The instrument creates `γ_N = 0` from a `γ_N = 2`
   root, 8 times, chains `4 → 2 → 0` (`(4, …, 2, …, 0)` in every one). So "AK(3) starts two
   steps away instead of one" does not by itself explain 0/40.
2. **The length exit is the barrier.** All 8 chains dip below 13 (minimum chain lengths
   5, 7, 7, 9, 9, 11, 11, 11): **0 of 8 stay in AK(3)'s band.** The same mechanism as §3, now on
   a root matched to AK(3) on rank, length *and* defect.
3. **Extra rank actively hurts at fixed budget.** 8/8 at rank ceiling 2 and **0/32** at
   ceilings 3–6. On an easy root (γ_N = 1, one move from a certificate) the rung structure is
   invisible; on a root at AK(3)'s difficulty, opening rank space costs the search every hit it
   had. This is the S-line question answered in the unhelpful direction, at this budget.

## 6. Verdict on AK(3)'s 0/40

**(c), which then collapses into (b).** The control passes the T-S19 creation test cleanly —
39 creations, 39/39 chains replayed from a verified `γ_N = 1` root — so S5's instrument is not
the `S16` instrument and its null is not void for that reason. It fails a different and equally
fatal test: the certificates it creates are not certificates AK(3) could have. Every one of the
39 rests on a rank-2 core of total length 8 or 11, and by Havas–Ramsay any member of AK(3)'s
class down there settles the open problem outright; S5's own length criterion (padded total
length ≥ 13) does not exclude these, because inert `AC4` discs inflate total length without
changing content. Controlling for the exit properly, the created rate is **2/40 = 0.050** at
the most generous reading and **0/40** at the structural one — and the freshly built control
matched to AK(3) on rank, length **and** defect (`⟨x,y | YYYxx, YYXYxyyx⟩`, γ_N = 2, AC-trivial)
scores **0 in-band creations in 40 runs** while still creating 8 out-of-band ones. **Expected
hits in 40 AK(3) runs: 40 × 0.050 = 2.0 at the generous rate, 40 × 0.000 = 0 at the matched
control's rate.** Observing **0** is what the control predicts under either accounting, so
`S5` §5.2's headline — "AK(3)'s stable class does not contain one that this search reaches even
once" — is a statement about the search's only working mechanism being unavailable to AK(3) by
hypothesis, not a fact about AK(3). No p-value is quoted, per
`experiments/lessons/contrast-length-confound.md` rule 3 and because the 40 runs are 8 seeds ×
5 rungs from a *single* root, not 40 independent draws (25 distinct witnesses, 2 distinct
cores, and all eight `k = 0` hits are the same state found by the same single move).

**S5 §5.2's status should be downgraded from "IS informative, within its budget" to
"uninformative for the same reason as §5.1".** What survives S5 intact: the build, the
three-route verification stack (0 anomalies), the exact-census audit of §4.5, the rank-8/rank-9
verified `γ_N = 0` witnesses of §4.3, and — newly — the demonstration that the move set *can*
create `γ_N = 0` from both `γ_N = 1` and `γ_N = 2` roots, which is more than any other
instrument on this line has shown.

## 7. Status of every claim in this file

| # | claim | status |
|---|---|---|
| §1 root defects (both families, k = 0…4) | exact census in this clone, `s18_roots.json` | **measured** |
| §2 replay fidelity 40/40 | compared to the persisted rows field-by-field | **measured** |
| §2 39 created / 0 inherited, chain defect sequences | chains reconstructed by a forwarding wrapper, every node decided | **measured** (chains **reconstructed**, not imputed) |
| §3 `tietze` core rank 2 / length 8 or 11 for 39/39 | computed, cores re-decided (all defect 0) | **measured** |
| §3 `elim` reduction is stable-AC legal at rank > 2 | needs the stable ambient automorphism principle beyond rank 2 | **[ASSERTED]**, `FRAMING.md` trap 2 |
| §3 "AK(3) cannot go below 13" | Havas–Ramsay via `FRAMING.md` §1; a sub-13 member settles the problem | **cited**, not re-verified this session |
| §4 rank histogram; the 17-vs-25 correction | recounted from the rows | **measured** |
| §5 defect-4 sources exist; the 260-member scan | exact census per member | **measured** |
| §5 defect-matched ladder 8/40, 0/8 in band, 0/32 at k ≥ 1 | new run, same protocol and budget | **measured**, bounded budget |
| §6 verdict | follows from §§1–5 | **established**, and it is a statement about the INSTRUMENT |

Bound direction, restated: every rate here is a **detection/creation rate of an
upper-bound-only instrument**. Nothing in this file bounds `γ_N` on AK(3)'s stable class from
below, and the corrected reading of S5 §5.2 removes a claim that was drifting that way. A
search that finds nothing bounds nothing.
