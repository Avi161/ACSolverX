# RESULTS — AK(3) stable AC-triviality campaign (live log)

Companion to [`PLAN.md`](PLAN.md). Newest entries at the bottom of each phase section.
Every claim is tagged with how it was verified.

---

## Literature status (session research, 2026-07-05)

**Headline: the published "proof" that AK(3) is stably AC-trivial is gapped, and the gap
is a concrete open problem we are attacking.**

Timeline reconstructed from primary sources:

1. **Shehper et al., arXiv:2408.15332 v1 (27 Aug 2024)** — abstract: *"we demonstrate that
   one of the potential counterexamples due to Akbulut and Kirby, whose status escaped
   direct mathematical methods for 39 years, is stably AC-trivial."* The chain:
   AK(3) ~AC~ P25 (their new 53-move AC′ path) and P25 ~stAC~ M3, an instance of the
   3-generator family of MMS02 Theorem 1.4 — which MMS02 claimed stably AC-trivial.
2. **Lisitsa, arXiv:2501.18601 (17 Jan 2025)** — "alternative proofs" via Prover9:
   sequences S1–S5 certifying P ~AC~ AK(3) where P is **byte-identical to P25** (checked
   letter-by-letter this session, under a↔x, b↔y). Stable triviality of P is justified by
   citing the same MMS02 result. Supplementary: zenodo.org/records/14567743.
3. **Shehper et al. v2 (11 Feb 2025)** — **claim rescinded** (abstract no longer mentions
   it; footnote 26 explicitly calls AK(3) a potential counterexample to the *stable* AC
   conjecture). New Appendix F: MMS02's 3-generator family was derived from a
   **misprinted** Wirtinger presentation W′ (13th relator `x13 = x5 x12 x5⁻¹`; the true
   diagram gives `x13 = x4 x12 x4⁻¹`). W′ is not the Wirtinger presentation of any knot
   diagram (deleting different relators yields different groups — e.g. B₃ vs ℤ), so MMS02
   Thm 1.4's stable-triviality argument (Reidemeister moves realized as stable AC moves)
   does not apply: *"these presentations are not necessarily stably AC-trivial."*
   Lisitsa's paper, written between v1 and v2, inherits the same gap and has not been
   corrected (no erratum found as of 2026-07-05).

What remains valid and machine-checkable:
- AK(3) ~AC~ P25: 53 explicit h-moves (v2 lines 3088–3090) + Lisitsa's S2 (160 steps).
- P25 ~stAC~ M3 (one Lemma-11 elimination, z = y⁻¹x).
- Prop 12 (v2 Appendix E): descendants of *correct* unknot Wirtinger presentations are
  stably AC-trivial by construction. The corrected W (Fig 24) is printed in v2.

**Open gap ⇒ our target: prove P25 (⟺ M3 ⟺ AK(3)) stably AC-trivial.**

---

## P0 — Existing pipeline verification (HARD gate) — ✅ PASSED 2026-07-05

- Fixed stale module paths (baseline_n2 moved by commit 8d69bd2 but two test files still
  pointed at the old nested location): `tests/phase2_test.py:33`,
  `tests/phase2_independent_test.py:40` → `experiments/stable_ac/baseline_n2`.
- `pytest tests/phase2_test.py tests/phase2_independent_test.py
  tests/ak3_words_independent_test.py` → **43/43 PASSED** (19.2 s).
  Includes: n=2 neighbor-set equivalence vs. the original notebook solver, n=2
  solved-set differential oracle on 12 dataset presentations, n=3 move validity vs.
  brute force, canonical-form invariance + key round-trips, null-revert block efficacy,
  persistence→replay closure, stabilization contract (byte-identical to `stabilize.py`).
- `tests/hard_words_independent_test.py` is a script-style suite (own Recorder/main;
  pytest's collection can't inject its `rec` argument — the 3 pytest "errors" are an
  invocation artifact, not failures). Run as intended:
  `python tests/hard_words_independent_test.py` → **6,068 checks passed, 0 failed**.
- Environment: repo venv Python 3.14.3, numpy 2.4.6, numba 0.66.0; installed pytest 9.1.1,
  sympy 1.14.0 into the venv (test/verification tooling only).

**Verdict: the existing greedy/stabilization machinery is verified at the same rung as
the shipped results claim (n=2 cross-implementation; n=3 brute-force + structural;
gold JAX gate still N/A for n=3 as documented). Safe to build on.**

## P4 — Move semantics gold gate — ✅ PASSED (strongest possible level)

- `hmoves.py` h1–h12 transcribed from Appendix B; `probe_appendix_f.py` replayed the
  printed 53-move Appendix-F path from P25 under all 4 order/inverse conventions:
  **forward order, forward moves lands EXACTLY on AK(3)** — equal as ordered word
  pairs, no canonicalization needed; the reverse replay (inverse moves, reversed)
  recovers P25 exactly. |abelianization det| = 1 at all 53 intermediate states; max
  total length along the path = 25 (the path fits comfortably in the solver's L=24
  per-relator cap).
- This machine-verifies at once: our concat/conjugation semantics (free-reduce only),
  the P25/AK3 transcriptions, and Shehper et al.'s Appendix-F claim P25 ~AC~ AK(3).
- Certificate emitted + verified + tamper-rejected:
  `results/stable_ac/ak3_stable_proof/certs/appendixF_P25_to_AK3.json` (53 steps).

## PL(partial) — Lisitsa S2 independently validated (+ 2 defects found in his data)

- Zenodo record 14567743 downloaded (6 files). `check_lisitsa_s2.py`: all 159
  transitions of the published S2 are valid AC moves (INV / MULT / CONJ, with the
  CONJ conjugator = the part after the X separator, states defined up to cyclic
  rotation); start = P25 exactly, end = AK(3) exactly; |det|=1 on every line.
  **RESULT: PASS** — Lisitsa's AC-bridge P25 ~AC~ AK(3) is genuine.
- Two defects found in the published artifact (worth reporting upstream):
  (1) line 91 contains `??` in relator 2 (corrupt state; bridged by composing the two
  adjacent moves — checks out); (2) line 81's CONJ label prints a left part that is
  not the inverse of the right part (the right part is the true conjugator).
- MMS02 misprint **confirmed verbatim at the source** (arXiv:math/0302080 PDF):
  relator 13 reads `x13 = x5 x12 x5^-1`. MMS02's commutator convention pinned:
  `[a,b] = a b a^-1 b^-1`. Lisitsa's paper confirmed to justify P's stable
  triviality solely by citing MMS02 Thm 1.4 (the misprint-broken theorem).
- Corrected-W transcription settled by RENDERING the actual PDF page 44 (the txt
  extraction scrambles superscripts; 3 relators were mis-transcribed in a first pass):
  W differs from MMS02's print ONLY in relator 13 (`x4 x12 x4^-1`), exactly as
  Appendix F states. Encoded in `wirtinger.py::W_CORRECTED`.

## P5 — Wirtinger cascade + certified descendant catalog — ✅ ENGINE VALIDATED

- `wirtinger.py::paper_family()` (delete r6; Lemma-11 eliminate x1..x5,x7..x9,
  x11..x13; rename x10,x14,x6 → x,y,z) **reproduces the paper's printed corrected
  3-generator family exactly** (both relators match the Section 9.2.2 formula up to
  rotation/inversion under MMS02's commutator convention; w = x10^-1 x14 x6 passes
  through untouched and lands as x^-1yz). Cross-source validation of the elimination
  engine.
- Eliminating z via w yields **P25corr** — the corrected analog of P25: a certified
  stably-AC-trivial 2-generator presentation, total length 76 (relators 33+43),
  |det|=1, full certificate verifies (`probe_cascade.py`). Not canonically equal to
  P25 or AK3 (expected; the misprint materially changed the family).
- `catalog.py`: randomized cascades (delete-k × w-bank × elimination order) generate
  certified 2-generator leaves, deduped by relabel-canonical key. First 32k iterations:
  **334 unique certified leaves** (151 fit the L=24 search cap; 141 content-rich with
  total length ≥ 10; histogram peaks at total length 20–40). No leaf is canonically
  equal to AK3 or P25 (no instant win).

## Lane A — first MITM searches (local pilots)

- From AK3 (100k nodes) and P25 (300k nodes) toward all catalog leaves
  (symmetry-expanded target sets, 953–1177 keys): **no hit yet**; both searches
  plateau at min_total_len = 13 (the familiar AK(3) hump floor — P25 falls into the
  same basin, consistent with its 53-move AC-connection to AK3).
- Next: reverse searches (leaf → {AK3, P25}×8), and ball-intersection escalation
  (dump the full 1M-node visited set of AK3/P25, test leaf-side searches against it).

## PL — Verify Shehper v2's analysis itself — ✅ ALL CHECKS PASS (2026-07-05 night)

`verify_literature.py` (completed by a background verification agent; machine-readable
results in `results/stable_ac/ak3_stable_proof/literature_checks.json`, 7/7 PASS):
- [X] Corrected W: **all 14** single-relator deletions present ℤ (exact SNF of the
      exponent matrix + S3 hom-count + ⟨x₁⟩ coset index 1). W is a genuine unknot
      Wirtinger presentation — Prop 12 applies to its descendants.
- [X] Misprinted W′: deleting r7 yields **12 S3-homs, 6 non-abelian** (a non-abelian
      image PROVES the group ≠ ℤ; the S3 fingerprint matches B₃ as v2 states), while
      deleting r14 is ℤ-consistent — different deletions give **different groups**, so
      W′ is not the Wirtinger presentation of any knot diagram. The misprint's operative
      content is confirmed. (Nuance: W′ del r12 has ℤ's S3-fingerprint — the draft's
      over-specific gate was corrected to the r7-vs-r14 disagreement, which is exactly
      the paper's "B₃ vs ℤ" signature.)
- [X] AK(3) presents the trivial group (coset enumeration, order 1).
- [X] M3 --(z:=y⁻¹x, Lemma-11)--> **exactly P25**, pinning MMS02's commutator
      convention [a,b]=aba⁻¹b⁻¹.
- [X] Corrected 3-gen family presents ℤ; adding w=z trivializes (order 1). Remark-17
      conjugation forms reproduce r1corr/r2corr.
- [X] MMS02 original: misprint confirmed verbatim at the source (see PL(partial)).
- [X] Lisitsa PDF → `literature/txt/lisitsa_ak3_stable_revisited.txt` + README index entry.

**The v1→v2 rescission story is now independently verified end-to-end: the gap is real,
and AK(3) stable AC-triviality is genuinely open.**

## Leaf classification — all in-cap catalog leaves are plain-AC-trivial (2026-07-05)

`classify_leaves.py` @50k nodes over the 151 leaves fitting L=24:
**151 ac_trivial / 0 stuck / 0 hit.** Every certified Wirtinger descendant that fits the
search cap is greedy-trivializable with ORDINARY AC moves — consistent with the paper's
Conjecture 18 (unknot-derived presentations are AC-trivial), and strategically decisive:
a MITM connection AK3 → leaf would prove AK3 **AC**-trivial, far stronger than the stable
claim we need and believed false. **Lane A is therefore deprioritized in favor of the
stable lanes (B and D), which work modulo stabilization.** (Lane A stays alive at low
priority on the C box for the ball-dump escalation.)

## Lane B — StableSolver validation + first runs (2026-07-05)

- `stable_solver.py`: best-first over substitution ⊕ stabilize(z=w bank) ⊕ Lemma-11
  eliminate, variable n_gen ≤ max_gen, gen-penalized priority; retraced solutions emit
  certificates automatically.
- Validation: MS idx-0 solves in 1 node **via eliminate** (destabilization works inside
  the search); **M3corr solves in 3 nodes** with a certificate that PASSES the verifier
  (`certs/laneB_M3corr_hero8_500.json` — an end-to-end stable-trivialization found by
  search, chain checked step-by-step). Measured 24 KB/node, 1.3k nodes/s → 1M-node runs
  need ~24 GB (Colab-tier; local caps at ~500k).
- AK3/P25 hero8 @20k and @50k: unsolved, min_total_len = 13 — the hump floor persists
  under the stable move set at small budgets (the z-relator immediately re-eliminates;
  escaping needs the search to climb the hump WITH the extra generator, hence the big
  budgets + gen_penalty grid queued for tonight/Colab).

## Lane D — plateau elimination (NEW, 2026-07-05 night) — the sharpest lane

**Insight.** Greedy on the stabilized 3-gen AK3 plateaus at total length 13 because it
cannot destabilize. But every visited 3-gen state with a generator occurring exactly
once in some relator admits a Lemma-11 elimination to a **2-generator presentation
stably-AC-equivalent to AK(3) by construction**. These quotients have never been
searched. If plain greedy trivializes ANY of them, AK(3) is stably AC-trivial — and the
whole chain (stabilize → substitution path → eliminate → greedy path) is one verifiable
certificate. All 151 catalog leaves being greedy-easy shows 2-gen trivial-group
presentations are often solvable even when related 3-gen forms are stuck.

- `plateau_elim.py`: harvest (full visited set → eliminations, deduped) / merge
  (signed-relabel symmetry dedup, AK3/P25 classes dropped, ranked by length) / solve
  (shortest-first 2-gen greedy, Pool, resumable) / on solve: full chain certificate
  built + verified automatically.
- Smoke @3k harvest (textbook, z=xyx): 124k visited → 29,672 raw → 15,827 unique
  candidates; **shortest at total length 14** (vs AK3's 13) — the elimination surface is
  rich. Quick full-pipeline test (10 words @4k): candidates at length 13 (1), 14 (5),
  15 (62); 754 shortest attempted @2k nodes, 0 solved (budget-limited by design).
- **Certificate chain gate PASSED**: with an easy start substituted in, a solved
  candidate's full chain (stabilize + substitution path + eliminate + greedy path +
  sign-fix inverts) verifies, and a semantic tamper (interior letter flip in a long
  relator) is rejected. (Note: sign-flipping a length-1 relator is canonically an AC2
  inversion — a correct accept, caught and documented while hardening the tamper test.)
- **Overnight run in flight**: 20 harvests (textbook+rep × hero8+r1+r2) @150k nodes —
  each yields ~5.9M visited states and ~916k unique candidates — then global merge and
  solve of the shortest ~6k+ candidates @25k, escalation @200k queued behind it.

**Night pass 1 result (2026-07-06 ~00:30):** 20 harvests → 8,339,784 raw candidates →
**74,489 unique-mod-symmetry** (total_len ≤ 24; AK3/P25 canonical classes dropped).
Length histogram floor: 13×1, 14×5, 15×68, 16×69, 17×376, 18×412, 19×2062, 20×2123.
All **931 candidates with total_len ≤ 18 attempted @25k nodes: 0 solved — and every
single one bottomed out at min_total_len = 13 exactly** (the AK(3) hump floor), whether
the elimination removed z (423 cases: can be an unwind of the stabilization, so same AC
class expected) or x/y (508 cases: genuinely class-moving eliminations). Interpretation:
the stable class has one deep basin with floor 13 from every entry point sampled so far —
the hump is a property of the class, not of the AK3 start state. Escalation @200k on the
≤16 pool (143 candidates) runs next; Colab boxes attack the 12,000 shortest @50k.

## P6 — Independent adversarial verifier — ✅ PASSED (2026-07-05 night)

An adversarial subagent authored `independent_verifier.py` + `tests/ak3sp_independent_test.py`
**black-box from the schema+math spec only** (forbidden from reading any engine module; imports
json+sys only; built its own free/cyclic reduction, Bareiss determinant, canonicalization and
step replay). Results: **20,947 checks passed, 0 failed; all 18 real certificates pass BOTH
verifiers** (appendixF 53-step, laneB × 3, 14 catalog leaf certs incl. an n_gen=14 start).
Mutation sensitivity confirmed (sign flips, corrupted targets, swapped states, mis-pointed
eliminate → all rejected). One accepted "mutation" was hand-verified to be a genuinely valid
alternative move, not a soundness hole. Spec ambiguities it resolved (canonicalization is
length-preserving; eliminate recomputes from state, ignores recorded params; end_is_trivial is
sign-insensitive) match the engine's semantics. **Every future solve-claim must pass both
verifiers — the gate is now in place.**

## Overnight infrastructure (2026-07-05 → 06)

- `night_lanes.py`: waits for Lane D, then runs Lane D escalation (@200k), Lane B grid
  (300k hero8 g3/g4/p1 + 100k full bank + 500k escalations), Lane C dumb baselines
  (trivial-z n=3/4/5, 0.4–1M) — each in a fresh forked child (peak-RSS released),
  streaming to `runs/night_lanes.jsonl`.
- Colab handoff: `run_lanes.py` + `nb_ak3_lanes.ipynb` — 5 boxes (D1/D2/D3 = Lane D at
  scale: 500k harvests, 12k solves @50k, full word bank on D3; B = StableSolver @800k;
  C = baselines @0.8–2M + MITM @2M with ball dumps). Quick base-case mode verified
  locally end-to-end for B and D1. Resumable on Drive; certs land in `<box>/certs/`.
