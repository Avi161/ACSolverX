# AK(3) Stable AC-Triviality — verify the literature, close the gap, certify the proof

**Folder:** `experiments/stable_ac/ak3_stable_proof/` (code) + `results/stable_ac/ak3_stable_proof/` (runs/certs).
**Branch:** `test/stable-ac-moves` (main checkout, no worktree).
**Live status log:** `[RESULTS.md](RESULTS.md)` — every gate, verification outcome, and run result is appended there as it happens.

---

## 1. The problem, precisely

AK(3) = ⟨x,y | x³y⁻⁴, xyxy⁻¹x⁻¹y⁻¹⟩ is a balanced presentation of the trivial group — the
flagship potential counterexample to the Andrews–Curtis conjecture. The **stable** AC
conjecture also allows stabilization moves:

- **AC4** add a new generator z and relator z; **AC5** remove such a pair (inverse).
- **Lemma 11** (arXiv:2408.15332, §9): if ⟨x₁..xₙ, y | r₁..rₙ, y⁻¹w⟩ presents the trivial
group (w a word in the xᵢ), it is stably AC-equivalent to ⟨x₁..xₙ | rᵢ[y:=w]⟩. This
justifies both *generalized stabilization* (add z with relator z·w⁻¹) and *elimination*
(a relator in which some generator occurs exactly once lets you remove that generator).

**Goal: prove AK(3) is stably AC-trivial, with a machine-checkable certificate.**

## 2. Literature status (established + verified this session)


| Event                                             | Claim                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Shehper et al. arXiv:2408.15332 **v1** (Aug 2024) | Abstract: AK(3) "**is stably AC-trivial**" — proof chained AK(3) ~~AC~~ P25 ~~stAC~~ M3 ∈ MMS02-Thm-1.4 family, "stably trivial by [MMS02]"                                                                                                                                                                                        |
| Lisitsa arXiv:2501.18601 (Jan 2025)               | "Alternative proof": Prover9 sequences for the same bridge AK(3) ~~AC~~ P25; stable-triviality of P25 justified by citing the same MMS02 theorem                                                                                                                                                                                   |
| Shehper et al. **v2** (Feb 2025)                  | **Claim rescinded.** Appendix F: MMS02's family came from a *misprinted* Wirtinger presentation W′ (relator 13 `x5·x12·x5⁻¹` instead of `x4·x12·x4⁻¹`); W′ is not a Wirtinger presentation of any knot, so MMS02 Thm 1.4's stable-triviality proof is broken. Footnote 26: AK(3) is again a potential counterexample to stable AC. |


What survives, twice-derived and machine-verifiable:

- **AK(3) ~~AC~~ P25** = ⟨x,y | x⁻¹y⁻¹xy⁻¹x⁻¹yxy⁻²xyx⁻¹y, y⁻¹x⁻¹y²x⁻¹y⁻¹xyxy⁻²x⟩
(53 explicit AC′ h-moves, paper lines 3088–3090; independently Lisitsa's 160-step S2).
- **P25 ~~stAC~~ M3** = ⟨x,y,z | x = z·[[y⁻¹,x⁻¹],z], y = x·[[y⁻¹,x⁻¹],z⁻¹]·[z⁻¹,x], x⁻¹yz⟩
(one Lemma-11 elimination, z = y⁻¹x).
- **Prop 12** (valid): delete any one relator from a *correct* unknot-diagram Wirtinger
presentation, add any word of exponent sum ±1 → stably AC-trivial by construction; and
Lemma-11 descendants inherit that certificate.

**⇒ The open gap: prove P25 (⟺ M3 ⟺ AK(3)) stably AC-trivial.** Prior in-repo sweeps
(0/388 solves, plateau at total length 13) could never close it: greedy substitution
alone cannot perform the Lemma-11 elimination supermove.

## 3. Attack lanes

- **Lane A (meet-in-the-middle via certified family).** Generate a large catalog of
2-generator presentations *certified stably-AC-trivial by construction* (corrected
Wirtinger W → delete relator k × add word w (exp-sum ±1) × Lemma-11 elimination
orders). Then search for an ordinary-AC connection between the catalog and the
{AK(3), P25} component with the tuned n=2 greedy (target-set termination).
One hit ⇒ trivial ~~stAC~~ descendant ~~AC~~ AK(3) ⇒ **done**.
- **Lane B (direct stable-move search).** Best-first search whose move set = substitution
⊕ stabilize(z=w from bank) ⊕ eliminate (Lemma 11), ≤5 generators, from M3, P25, AK(3),
and the captured plateau-13 states. Reaching the trivial presentation ⇒ **done**.
- **Lane C (mentor's dumb baselines).** ⟨x,y,z | r1,r2,z⟩ (empty w — *never swept before*)
and 4/5-generator trivial-z variants, current greedy. Cheap, scientifically required.
- **Lane D (plateau elimination — added after authoring; the sharpest lane).** Harvest the full
visited set of greedy on a stabilized AK(3) form, Lemma-11-eliminate every visited 3-gen state
with a once-occurring generator → fresh **2-generator** presentations ~~stAC~~ AK(3) *by
construction*, then plain n=2 greedy-solve the shortest. Any solve ⇒ **done**. This is what
boxes D1/D2/D3 run (`plateau_elim.py`); it searches the 2-gen quotients no prior sweep touched.
- **Lane E (RL beam).** Pretrained 610model Dual-Ring policy + beam search over the floor set
(run locally; 0/185).

Every claimed solve must replay end-to-end under an **independently authored verifier**
(adversarial subagent, black-box from the certificate spec + the math only).

## 4. Phases & gates (TODO checklist — reconciled against RESULTS.md, 2026-07-06)

- [x] **P0** Fix stale `baseline_n2` test paths; all suites green. **HARD GATE**
  ```
  → ✅ 43/43 pytest + 6,068 script-suite checks (RESULTS §P0).
  ```
- [x] **PL** Verify Shehper v2's own analysis: corrected-W vs misprinted-W′ quotient checks;
  ```
  M3/P25 present trivial group (coset enumeration); MMS02 misprint confirmed at source;
  Lisitsa PDF → `literature/txt/`. *(user demand: "verify what Shehper said is correct")*
  → ✅ 7/7 checks (`literature_checks.json`); v1→v2 rescission verified end-to-end.
  ```
- [x] **P1** `presentation.py` — variable-n_gen states, `canonical_key_g`,
  ```
  `relabel_canonical_key` (k≤2 only), exact `abelianization_det` (must stay ±1 under
  every move — independent global invariant).
  → ✅ built; |det|=1 held at all 53 App-F states and every Lisitsa-S2 line.
  ```
- [x] **P2** `stable_moves.py` + `certificate.py` — stabilize/eliminate emitting cert steps;
  ```
  gate: eliminate∘stabilize == identity (100 random cases) + det preserved. **HARD GATE**
  → ✅ engine validated via Lane B (eliminate solves MS idx-0 in 1 node, M3corr in 3) + P6.
  ```
- [x] **P3** `verify_certificate.py` (own draft) — replay + precondition + global checks;
  ```
  tampered certs rejected.
  → ✅ tamper-rejection confirmed (P4 + P6 mutation tests).
  ```
- [x] **P4** `hmoves.py` + `certs/appendixF_P25_to_AK3.json` — replaying the paper's 53
  ```
  h-moves from P25 **must land exactly on AK(3)**. Cross-source gold oracle for our
  move semantics; nothing ships to Colab before this passes. **HARD GATE**
  (SOFT: h0-index hypothesis via the Appendix-B 381-move path; Lisitsa Zenodo S2 replay.)
  → ✅ lands EXACTLY on AK(3) (fwd order/fwd moves), reverse recovers P25; cert verified + tamper-rejected.
  ```
- [x] **P5** `wirtinger.py` — corrected W transcription test; certified descendant catalog
  ```
  (each leaf ships its own verified certificate).
  → ✅ `paper_family()` reproduces the printed 3-gen family; `catalog.py` → 334 certified leaves.
  ```
- [x] **P6** `mitm.py` (TargetSolver, symmetry-expanded targets) + **independent adversarial
  ```
  verifier** authored by a subagent from spec only; all certs pass BOTH verifiers. **HARD GATE**
  → ✅ 20,947 checks, all real certs pass BOTH verifiers.
  ```

- [X] [-] **P7** `lane_worker.py` + Colab notebook(s) — 5 boxes × 50 GB, all cores (fork Pool,
maxtasksperchild=1), crash-safe resumable JSONL + Drive sync; local base-case cell.
**Planned:** boxes A1/A2/A3/B/C (MITM-outward + 2 MITM-reverse shards + direct + dumb) across
three notebooks. **Actual:** one `nb_ak3_lanes.ipynb`, boxes **D1/D2/D3/B/C** — Lane D
(plateau elimination, discovered after this plan was written, §3) became the three D boxes and
MITM was folded into box C. Reason: Lane D is the sharper attack and one notebook can drive all
five runtimes. → ✅ built (`run_lanes.py` + `nb_ak3_lanes.ipynb`); base-case verified locally for B & D1.
- [X] [-] **P8** Run lanes (user runs Colab; Lane B/C + M3 change-of-variables run locally);
verify hits end-to-end; final writeup in RESULTS.md.
→ **local DONE**: Lanes A–E all run, 0 solved — the whole accessible stable class floors at
total length 13 (+k for extra trivial generators); CONCLUSION written; two-floor {AK3, F}
structure found + F→AK3 cert. **PENDING (user):** the Colab 5-box escalation at 10–40× budgets
(`nb_ak3_lanes.ipynb`) — the only step left to escalate the negative or find a solve.

## 5. Colab arm sizing (5 × 50 GB high-RAM boxes, all cores) — AS BUILT

Superseded the A1/A2/A3 MITM-box scheme (see P7 `[X][-]`); the shipped boxes, per
`run_lanes.py` + `nb_ak3_lanes.ipynb`:


| Box | Arm                                          | Grid                                                                  | Budget / workers                |
| --- | -------------------------------------------- | --------------------------------------------------------------------- | ------------------------------- |
| D1  | Lane D, `textbook`+`p25` forms               | harvest 10 z=w words → Lemma-11 eliminate → solve top 12,000 shortest | 500k harvest / 50k solve, W≈4/8 |
| D2  | Lane D, `rep`+`floorF` forms                 | same                                                                  | 500k / 50k, W≈4/8               |
| D3  | Lane D, FULL ~95-word bank, `textbook`+`rep` | harvest → eliminate → solve top 10,000                                | 200k / 25k, W≈4/8               |
| B   | direct stable-move (StableSolver)            | AK3/P25, g≤3/4, hero8/full stabilize bank, gen_penalty 1/2            | 800k (×4) + 300k (×2), W=2      |
| C   | dumb baselines + MITM-outward                | trivial-z n=3/4/5 both forms + MITM AK3/P25 (ball dumps)              | 0.8–2M, W=2                     |


Sizing anchors (measured, prior runs): n=3 greedy ≈ 6.8 KB/node, 2.8–4.9k nodes/s.
Escalation: box C dumps AK3/P25 2M-node visited balls (`balls/ball_*_2M.gz`) → intersection re-search.

## 6. Reuse map

`one_generator/greedy_nrel.py` (solver, canonical form, byte keys, path sidecars,
verify_path), `one_generator/stabilize.py` + `ak3_words.py` (z·w⁻¹ transform, 95-word
bank, AK3 forms), `baseline_n2/jsonl_io.py` (`jsonl_done_ids`/`jsonl_append`),
`one_generator/ak3_probe.py`/`run_ak3_wormhole.py` (pickle-safe worker + fork-Pool driver

- resume pattern), `baseline_n2/greedy_ac.py` (n=2 differential oracle, tests only).

## 7. Risks

- App-F replay fails → free-vs-cyclic reduction or move-direction semantics wrong; the
paper's endpoint is the oracle; fix before any Colab spend.
- h0 undefined in paper's h-table → only blocks the optional 381-move replay (the
53-move path uses h1–h12 only — verified token-by-token).
- Elimination length blowup → `l_cap=64`, over-cap branches dropped + logged.
- All lanes fail in budget → deliverable is still: green suites, independently-verified
stable-AC engine + certificates, the verified literature-gap writeup (v1 claim →
Lisitsa inheritance → v2 rescission), and a certified descendant catalog for future runs.

