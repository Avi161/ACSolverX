# Theory results, overnight run 2026-07-21 (branch `research/stable-ac-escape`)

Committed summary of the night's two formal results; the full proofs live in `literature/proofs/STABLE_AC_NEW.tex` §4–§5 (local-only by the repo's gitignore — Lemma 6, Theorem 7, Corollaries 8–9, Proposition 10, compiled PDF alongside). Verification scripts ran offline over the committed sweep jsonls; no search above 1,000 nodes anywhere.

## 1. The multi-substitution CoV length law (n_subs = k ≥ 2) — PROVEN + CHECKED

All previously shipped length results covered single-substitution (k = 1) transformed-relator CoVs only. The new exact law, under no free cancellation, with `e = |expr|`, `p` = occurrences of the eliminated generator in `w`, `L = |w|`, `N_a` = its occurrences in the input pair:

`Δ = (e−1)(N_a−2) − (k−1)[(e−1)p + (L−1)]`

equivalently `Δ = (e−1)(Ñ_a−1) − (L−1)(k−1)` via the exact count identity `Ñ_a = N_a − 1 − (k−1)p` over the kept relators. Reduces to the shipped law at k = 1. With cancellation it becomes a ≤ bound with non-negative EVEN deficit. **Checked on every reconstructable n_subs ≥ 2 transformed-relator row of the committed sweeps: 1,995 distinct transforms (3,775 rows, n_subs 2–9), 0 violations; per-relator form checked on 3,990 relator outputs, 0 violations; exactly tight in 12.0%.**

Consequences: (a) the per-relator form extends the proven cap-fit **pre-filter** to the n_subs ≥ 2 candidates the restart tree actually needs; (b) the `−(k−1)[…]` term is the z-compression each extra substitution buys — **"CoVs go uphill" is a k = 1 phenomenon; multi-substitution CoVs (exactly the orbit-escaping ones) trend downhill.**

## 2. The orbit floor is NOT CoV-invariant — floor conjecture REFUTED

`μ(P)` = Aut(F₂)-minimal total length of P's orbit (`aut_canon`). Since n_subs = 1 and defining-relator CoVs stay in-orbit (shipped Thms), only n_subs ≥ 2 transformed-relator hops can move μ — and they can move it DOWN:

- **AK(2)** `⟨x,y | xxYYY, xyxYXY⟩`, μ = 11: one gated subword CoV (`z = Xy`, iso x/0, n_subs = 2) lands in a different, non-primitive orbit with **μ = 10**. Independently re-verified in this session.
- **ms640 solved row** `⟨YYYx, YYXyx⟩`, μ = 6: one hop (`z = yy`, n_subs = 2) lands the **standard orbit (μ = 2)**.
- Sampled sweep: μ-lowering hops on 6 of 15 inputs; descents can pass through UPHILL intermediates (one case descends 8→6 via a μ = 14 intermediate) — so a restart tree must not prune per-hop μ increases.
- **AK(3) is confirmed lateral-at-the-wall** (depth-3 reachable min μ = 13): the shipped AK(3) observation survives; only its universal generalization dies.
- **On the 124 (11,246 sweep rows): exactly 4 classes have a μ-descending hop-1** — aca_99, aca_100 (25→22), aca_105, aca_106 (25→24), all via `z = yy`; the other 120 are lateral-or-up at hop 1. Depth-2 map: `results/stable_ac/mu_scan/` (via `experiments/stable_ac/cov/mu_descent_scan.py`).

Search consequences shipped tonight: the `cov_mu_lex` portfolio strategy (μ-first candidate ranking) and the μ-ranked escape ordering inside `stall_escape.py`.

## 3. Obstruction barrier (folklore made precise) — see `OBSTRUCTION_BARRIER.md`

No invariant at or below the simple-homotopy layer can separate stable-AC classes of balanced trivial-group presentations (contractibility + Wh(1) = 0); any true obstruction must live strictly at the 3-deformation layer, which IS the open question. Don't spend compute on invariant-based pruning; the decidable 3-dimensional predicate is thickenability (`experiments/stable_ac/thickenable/NEUWIRTH_FEASIBILITY.md`, verdict GO).
