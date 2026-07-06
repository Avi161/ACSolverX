# AK(3) Stable AC-Triviality — verify the literature, close the gap, certify the proof

**Folder:** `experiments/stable_ac/ak3_stable_proof/` (code) + `results/stable_ac/ak3_stable_proof/` (runs/certs).
**Branch:** `test/stable-ac-moves` (main checkout, no worktree).
**Live status log:** [`RESULTS.md`](RESULTS.md) — every gate, verification outcome, and run result is appended there as it happens.

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

| Event | Claim |
|---|---|
| Shehper et al. arXiv:2408.15332 **v1** (Aug 2024) | Abstract: AK(3) "**is stably AC-trivial**" — proof chained AK(3) ~AC~ P25 ~stAC~ M3 ∈ MMS02-Thm-1.4 family, "stably trivial by [MMS02]" |
| Lisitsa arXiv:2501.18601 (Jan 2025) | "Alternative proof": Prover9 sequences for the same bridge AK(3) ~AC~ P25; stable-triviality of P25 justified by citing the same MMS02 theorem |
| Shehper et al. **v2** (Feb 2025) | **Claim rescinded.** Appendix F: MMS02's family came from a *misprinted* Wirtinger presentation W′ (relator 13 `x5·x12·x5⁻¹` instead of `x4·x12·x4⁻¹`); W′ is not a Wirtinger presentation of any knot, so MMS02 Thm 1.4's stable-triviality proof is broken. Footnote 26: AK(3) is again a potential counterexample to stable AC. |

What survives, twice-derived and machine-verifiable:
- **AK(3) ~AC~ P25** = ⟨x,y | x⁻¹y⁻¹xy⁻¹x⁻¹yxy⁻²xyx⁻¹y, y⁻¹x⁻¹y²x⁻¹y⁻¹xyxy⁻²x⟩
  (53 explicit AC′ h-moves, paper lines 3088–3090; independently Lisitsa's 160-step S2).
- **P25 ~stAC~ M3** = ⟨x,y,z | x = z·[[y⁻¹,x⁻¹],z], y = x·[[y⁻¹,x⁻¹],z⁻¹]·[z⁻¹,x], x⁻¹yz⟩
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
  One hit ⇒ trivial ~stAC~ descendant ~AC~ AK(3) ⇒ **done**.
- **Lane B (direct stable-move search).** Best-first search whose move set = substitution
  ⊕ stabilize(z=w from bank) ⊕ eliminate (Lemma 11), ≤5 generators, from M3, P25, AK(3),
  and the captured plateau-13 states. Reaching the trivial presentation ⇒ **done**.
- **Lane C (mentor's dumb baselines).** ⟨x,y,z | r1,r2,z⟩ (empty w — *never swept before*)
  and 4/5-generator trivial-z variants, current greedy. Cheap, scientifically required.

Every claimed solve must replay end-to-end under an **independently authored verifier**
(adversarial subagent, black-box from the certificate spec + the math only).

## 4. Phases & gates (TODO checklist, kept current)

- [ ] **P0** Fix stale `baseline_n2` test paths; all 4 existing suites green. **HARD GATE**
- [ ] **PL** Verify Shehper v2's own analysis: corrected-W vs misprinted-W′ quotient checks;
      M3/P25 present trivial group (coset enumeration); MMS02 misprint confirmed at source;
      Lisitsa PDF → `literature/txt/`. *(user demand: "verify what Shehper said is correct")*
- [ ] **P1** `presentation.py` — variable-n_gen states, `canonical_key_g`,
      `relabel_canonical_key` (k≤2 only), exact `abelianization_det` (must stay ±1 under
      every move — independent global invariant).
- [ ] **P2** `stable_moves.py` + `certificate.py` — stabilize/eliminate emitting cert steps;
      gate: eliminate∘stabilize == identity (100 random cases) + det preserved. **HARD GATE**
- [ ] **P3** `verify_certificate.py` (own draft) — replay + precondition + global checks;
      tampered certs rejected.
- [ ] **P4** `hmoves.py` + `certs/appendixF_P25_to_AK3.json` — replaying the paper's 53
      h-moves from P25 **must land exactly on AK(3)**. Cross-source gold oracle for our
      move semantics; nothing ships to Colab before this passes. **HARD GATE**
      (SOFT: h0-index hypothesis via the Appendix-B 381-move path; Lisitsa Zenodo S2 replay.)
- [ ] **P5** `wirtinger.py` — corrected W transcription test; certified descendant catalog
      (each leaf ships its own verified certificate).
- [ ] **P6** `mitm.py` (TargetSolver, symmetry-expanded targets) + **independent adversarial
      verifier** authored by a subagent from spec only; all certs pass BOTH verifiers. **HARD GATE**
- [ ] **P7** `lane_worker.py` + Colab notebooks `nb_laneA_mitm.ipynb`, `nb_laneB_stable.ipynb`,
      `nb_laneC_dumb.ipynb` — 5 boxes × 50 GB, all cores (fork Pool, maxtasksperchild=1),
      crash-safe resumable JSONL + Drive sync; every notebook has a local base-case cell.
- [ ] **P8** Run lanes (user runs Colab; Lane B/C + M3 change-of-variables run locally);
      verify hits end-to-end; final writeup in RESULTS.md.

## 5. Colab arm sizing (5 × 50 GB high-RAM boxes, all cores)

| Box | Arm | Grid | Budget / workers |
|---|---|---|---|
| A1 | MITM outward | greedy from AK3 & P25; target = all descendant keys (symmetry-expanded) | 1M nodes, W=2 (~7 GB each) |
| A2 | MITM reverse shard 0 | descendants idx%3==0 → targets {AK3,P25}×8 | 300k nodes, W=8 (~2 GB each) |
| A3 | MITM reverse shards 1,2 | descendants idx%3∈{1,2} | 300k nodes, W=8 |
| B | direct stable-move | M3, P25, AK3, plateau-13 starts; subst+stabilize+eliminate, ≤5 gens | 1M nodes, W=4 |
| C | dumb baselines | trivial-z 3/4/5-gen on both AK3 forms | 1M nodes, W=6 |

Sizing anchors (measured, prior runs): n=3 greedy ≈ 6.8 KB/node, 2.8–4.9k nodes/s.
Escalation: dump AK3 1M-node visited keys (~30 MB) → intersection re-search of survivors.

## 6. Reuse map

`one_generator/greedy_nrel.py` (solver, canonical form, byte keys, path sidecars,
verify_path), `one_generator/stabilize.py` + `ak3_words.py` (z·w⁻¹ transform, 95-word
bank, AK3 forms), `baseline_n2/jsonl_io.py` (`jsonl_done_ids`/`jsonl_append`),
`one_generator/ak3_probe.py`/`run_ak3_wormhole.py` (pickle-safe worker + fork-Pool driver
+ resume pattern), `baseline_n2/greedy_ac.py` (n=2 differential oracle, tests only).

## 7. Risks

- App-F replay fails → free-vs-cyclic reduction or move-direction semantics wrong; the
  paper's endpoint is the oracle; fix before any Colab spend.
- h0 undefined in paper's h-table → only blocks the optional 381-move replay (the
  53-move path uses h1–h12 only — verified token-by-token).
- Elimination length blowup → `l_cap=64`, over-cap branches dropped + logged.
- All lanes fail in budget → deliverable is still: green suites, independently-verified
  stable-AC engine + certificates, the verified literature-gap writeup (v1 claim →
  Lisitsa inheritance → v2 rescission), and a certified descendant catalog for future runs.
