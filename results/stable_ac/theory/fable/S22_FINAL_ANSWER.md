# S22 — The S-line's final answer: does arbitrary stabilization make hard presentations easier?

Branch `claude/stable-ac-conjecture-stabilization-rwo9as`. **This branch must be merged into
`fable/proof` by the user** — a cloud session can only push to its own `claude/*` branch, so
nothing here reaches `fable/proof` on its own. No PR opened (`FRAMING` trap 10).
**Note for the user: `fable/proof` does not currently exist on the remote** (`git ls-remote
--heads origin` lists no such branch), so it must be created before this can be merged there.

This supersedes `S13_SYNTHESIS.md` §1 as the session's answer. S13 remains as the working
record, including its retracted sections, which are kept verbatim.

---

## 0. The brief, and the answer in three sentences

*Does the stable AC conjecture get easier for hard presentations — AK(3), the 124 unsolved
Miller–Schupp classes — once rank grows well past 3? Use change of variables and Lemma 11.
Is there a simple general method?*

1. **No, and now with a mechanism rather than a null: adding generators is exactly inert.**
   `γ_N` does not move under stabilization at any rank (exact census, ranks 2–5), change of
   variables is a depth-1 phenomenon, and where extra rank was measured against a fixed
   budget it *hurt* — 0/32 at rank ceilings 3–6 against 8/40 at ceiling 2.
2. **A simple general method would be the conjecture itself, not a route to it** — stable AC
   is *equivalent* to "every balanced trivial-group presentation has a thickenable member in
   its stable class" (§2, conditional on Lackenby Thm 1.3).
3. **The one move that does exploit extra generators (SPLIT) is structurally the wrong
   tool**: it destroys thickenability certificates 7 times in 10 and has never created one in
   57,858 attempts, while plain AC2 creates them 14 times in 1,470 on *identical* parents.

**Nothing here proves or disproves the AC or stable AC conjecture.** Three headline claims
were retracted during the session; §4 is the record.

---

## 1. What was proved

| # | statement | status |
|---|---|---|
| **S15.1** | `γ_N(T_n) = 0` for every rank `n` — the standard presentation is thickenable | proved; machine-checked `n ≤ 6` |
| **S15.2** | every balanced trivial-group presentation is contractible, so **no homotopy invariant** can obstruct — any obstruction must be combinatorial | proved (not new: `R10` L1) |
| **S15.3** | **`γ_N` is not a stable-AC invariant** — `AK(3)` (`γ_N=2`) `~_st` `C1` (`γ_N=1`), chain re-verified. Kills the cleanest disproof idea on this line | proved by explicit witness |
| **S15.4** | the route is **one-sided**: Lackenby Thm 1.3 is an implication, so every instrument here bounds `Γ` from **above**; no null bounds anything below | proved (given Thm 1.3's *form*) |
| **S15.5c** | **stable AC ⟺ every balanced trivial-group presentation has a `γ_N = 0` member in its stable class** | proved, **conditional on Thm 1.3** (see §5) |
| **S19.1** | the `m` of **Lemma 11** *is* the algebraic / van Kampen **area** of `w` over the substituted relators — a spelling-independent, instance-computable invariant | proved; Lemma 11 **verified from source** this session |
| **S19.2b** | *every* single-destabilization realization costs `N ≥ log₂ Area` — closes the authors' second escape ("find a different proof") | proved |
| **S19.4** | a **computable uniform** bound on `m` exists **iff** Magnus's problem is decidable ⇒ that route is **BLOCKED** | proved, given the relayed openness of Magnus's problem |
| **S19.5** | `m*(L) ≥ L − 2`, unconditionally; also kills any bound in terms of rank alone | proved |
| **S20.1** | **non-planar link ⇒ `γ_N ≥ 1`** — the line's first certified *lower* bound. Falsification test: 945 `γ_N = 0` states, **945 planar, 0 non-planar** | proved + certified |
| **S3** | a chord refinement is a **CW subdivision**: `\|K_{P′}\| ≅ \|K_P\|`, entire defect histogram preserved | proved + audited |

**And the one that matters most for the brief**, measured rather than proved:

> **Stabilization is inert for `γ_N`.** Exact census: AK(3) holds `minimum_defect` 4 at ranks
> 2, 3, 4 **and** 5; two controls hold defect 2 across the same. Adding generators alone does
> not move `γ_N` at any rank. Only moves that *use* the new generators can.

## 2. What the brief asked for specifically

**Change of variables** — the whole `Aut(F_n)` orbit lies in `~^{(1)}`: one stabilization
realizes any change of variables (F1, proved). It is a **depth-1** phenomenon and buys
nothing at higher rank.

**Lemma 11** — verified from source (the authors' LaTeX re-cloned this session, not relayed),
and answered: its cost parameter `m` is an area (S19.1), the uniform effective bound the
authors ask for is **equivalent to a named open problem** (S19.4, route BLOCKED), and their
suggested alternative route is closed too (S19.2b). Family-specific bounds — AK(n), the
Miller–Schupp series — are untouched by this and remain legitimate targets.

**"A simple general way"** — by S15.5c such a construction *is* the stable AC conjecture on
balanced trivial-group presentations. Its absence after seven hours is not a defect of the
approach; any future candidate must be checked for a hidden reduction to the open problem
before it is believed.

## 3. The mechanism results — the session's real yield

**The cubic chord+SPLIT pipeline is certificate-preserving and certificate-non-creating.**

| | edges / states | creations |
|---|---|---|
| SPLIT `γ_N` transition table, all families | 174,178 edges | `1→0` **0** in 56,388 opportunities, from 1,958 distinct `γ_N=1` parents at ranks 9–12, chain depths 0–3 |
| states from five non-thickenable roots | 106,268 decided | **0** |
| **paired same-parent control, rank 5** | 1,470 | **AC2: 14. SPLIT: 0.** |

Shape facts (measured): every descent is by exactly 1 (`2→0`, `3→1`, `1→0` all empty) while
ascents jump by 2 (`0→2` = 650), so no `\|Δγ_N\| ≤ 1` law explains it; the descent rate
collapses 8.60 % → 0.94 % → **0 %** as the parent falls 3 → 2 → 1; and SPLIT **destroys**
certificates at 69.6 %, crossing the thickenability boundary 2,101 times downward and **zero**
times upward in 174,178 tries.

**The planarity obstruction is real but is not the explanation.** S20.1 is proved, but
(i) it bounds a *state's* `γ_N`, not `Γ` — `T_n` is planar, so no disproof route opens;
(ii) non-planarity is **not** preserved by SPLIT (explicit certified `K3,3` → verified sphere
counterexample); (iii) it is vacuous on AK(3) — AK(3)'s link is exactly `K4`, and every rank-2
link is planar; and (iv) only 16.9 % of the `γ_N=1` parents are non-planar while 47.5 % of the
56,388 edges have a *planar* child, so it explains at most half the empty cell.

**Therefore:** the cubic route is retired *with a mechanism* — but as an **instrument fact,
not a theorem**. No monotonicity result forbids reaching `γ_N = 0`, and the pipeline
demonstrably descends `2 → 1` (527 states in AK(3)'s own pool).

## 4. What was retracted — the honesty record

Three headline claims fell, all to the same underlying mistake at increasing depth. Recording
them because a future session that does not read this will make the fourth version.

| # | claim | why it fell |
|---|---|---|
| **S10** | certificates get commoner with rank | matched *total* length across ranks, so mean relator length fell with rank — it measured **length** (T-S10) |
| **S13 §3z-bis** | "the strongest result of the session": control 759/50,320 vs AK(3) 0/45,111 | the control was **already `γ_N = 0`** — it measured *survival*, not creation. All 759 hits have defect chain `(0,0,0,0)` (**T-S19**) |
| **S21** | matched defect-4 control 35/40 vs AK(3) 0/34 | the controls **exit the length band** — every hit walks *down* (witnesses at 3,4,5,…7) into a region AK(3) provably cannot enter, since any member of its class below length 13 would settle the problem (**T-S20**) |

Two further errors of mine caught by audit and worth carrying: a creation-rate denominator
that pooled 759 chains which *start* at the property (so are not creation opportunities); and
an `0/34` quoted from console output while two of its three runs were **still executing** —
the artifact-backed figure was `0/16`. *A number is measured when a file on disk contains
it.* Also: five runs sharing one `--seed` are not independent restarts.

**The deepest lesson (T-S20) is that this is not a fixable control design.** An auditor built
controls matched on every axis the instrument can see — no shared relator, no unit
abelianisation row, even matched on relator-length shape — and the rate did not collapse
(59/64). The incomparability is not an attribute of the control but the *route* it is allowed
to take: **any control you can verify is solvable is, by that verification, close to a
solution in a way an open target is not.** Target-versus-control cannot settle this question.

## 5. Sourcing, stated plainly

`literature/` is gitignored; this clone contains only `literature/fake_surfaces/` (checked by
`ls` while writing). **Lackenby Thm 1.3 is source-relayed, not read here** — S15.5b/c depend
on it and are flagged; everything else does not. **Lemma 11 is verified from source** this
session (`github.com/ammedmar/ac_paper` @ `d86984d`, `sec/stable.tex:28–38`), which is an
upgrade over the earlier 3-hop relay. Magnus's problem being open is **relayed, 3 hops**, and
is load-bearing only for S19.4's BLOCKED verdict.

## 6. Open leads, in the order I would take them

1. **A quantity monotone under *all* stable AC moves** remains unknown and is the whole
   disproof program. S15 §6 tabulates why every candidate so far is dead. Note S20.1 shows
   such a quantity need not be a homotopy invariant — it just has to survive SPLIT, which
   planarity does not.
2. **Family-specific bounds on Lemma 11's `m`** for AK(n) or the Miller–Schupp series —
   untouched by S19.4's blocking result, and S19.2a converts any such bound into an explicit
   AC move count. `Area_{AK(2)}(x) ≥ 4` is measured but the instrument **saturated**, so the
   true value is unknown.
3. **AC2, not SPLIT.** The paired control says plainly which move creates certificates.
   Any future high-rank search should be built on AC2-rich move sets.
4. **Instrument limits are now the binding constraint at depth ≥ 1.** Both depth ladders spent
   > 40 minutes inside depth 1 without completing it; `s12_hunt` writes its JSON only at the
   end, so an interrupted run yields nothing. High-rank hunting needs incremental persistence
   and a cheaper decider before the brief's regime is testable at all.
5. Q(F2) at `k ≥ 2`; Conjecture SR restricted to the trivial group; the untested
   entangled-slide mechanism (attempted four times, never completed — S13 §4b).

## 7. Status of this file

Every claim above is classified in its source document. Nothing here is a proof or disproof of
the AC or stable AC conjecture; the strongest positive results are S19's theorems on Lemma 11
and S20.1's certified lower bound, and the strongest negative results are the retractions and
the mechanism facts in §3.
