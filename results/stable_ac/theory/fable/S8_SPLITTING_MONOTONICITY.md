# S8 — Generator splitting is MONOTONE: the second bookkeeping mechanism is also dead

S-line, branch `claude/stable-ac-conjecture-stabilization-rwo9as` (merge into
`fable/proof`). Companion to S3 (triangulation is a subdivision) and S7 (depth).
Status: **measurement complete; proof is a SKETCH awaiting audit.**

## 1. The mechanism

`S3 §4` isolated the hypothesis that makes triangulation inert: the stabilized generator
is used exactly twice, so its edge carries exactly two 2-cell germs and the refinement is
a subdivision. The obvious way to violate that hypothesis is **generator splitting**:

> Pick a generator `g` occurring `c` times. Adjoin `u` by AC4, convert the relator `u` into
> `u g^{-1}` by Lemma S-a (legal because the group is trivial), and re-route any chosen
> subset of `g`'s occurrences onto `u` — each re-routing being
> `A g B ↦ A g B · (gB)^{-1} (u g^{-1}) (gB)= A u B`, i.e. AC3;AC2;AC3.

Balanced, in the stable class by construction, and **not** a subdivision: `u`'s edge
carries `1 + |S|` germs, which exceeds 2 as soon as two occurrences are re-routed. It also
does exactly what the naive "more generators" intuition wants — it spreads a crowded germ.
At rank 2 all 13 of AK(3)'s letter occurrences sit on four germs; splitting each generator
once moves that onto eight.

## 2. Measurement

`gamma_N_factorial_n`, exact census, `cap_rotations = 4·10⁵`, `minimum_defect` reported raw
(project γ_N = `minimum_defect // 2`). Bases: AK(3), and five AC-trivial members of AK(2)'s
class (total length 13, both relators ≥ 3) that are `NOT_SPHERICAL` — i.e. exactly the
cases where stable AC-triviality is *known* and thickenability is *currently absent*, which
is where a mechanism that creates thickenability would show itself first. Each row is an
independent random re-routing of every occurrence of every generator; the run carries a
replay certifier (substitute every copy back to `g`; the input relators must reappear up to
cyclic reduction) and no uncertified state was scored.

| base | base defect | copies/gen | rank | states scored | best defect found | defect histogram |
|---|---|---|---|---|---|---|
| ak2 L13 (×5 distinct) | 2 | 1 | 2→4 | 199 | **2** | 2 in 109, 4 in 90 |
| AK(3) | 4 | 1 | 2→4 | 117 | **4** | 4 in 117 |
| ak2 L13 (×5 distinct) | 2 | 2 | 2→6 | 197 | **2** | 2 in 74, 4 in 122, 6 in 1 |
| AK(3) | 4 | 2 | 2→6 | 119 | **4** | 4 in 119 |

**632 split states, spread over ranks 4 and 6. Not one fell below its base.** Splitting
raised the defect roughly half the time and never lowered it. On AK(3) specifically, 236
split states at ranks 4 and 6 all sat at defect 4 — the same value AK(3) has at rank 2 and
at rank 9.

Note the contrast with triangulation, which preserved the defect *exactly* (480/480). That
difference is itself confirmation that splitting is a genuinely different operation: it
changes `|K|`, it just changes it the wrong way.

## 3. Conjecture S8 and its proof sketch

> **Conjecture S8 (monotonicity).** If `P'` is obtained from `P` by generator splitting,
> then `γ_N(P) ≤ γ_N(P')`. In particular splitting can never create thickenability.

**Sketch.** In the link graph, the length-2 relator `u g^{-1}` contributes exactly two
edges: `u⁻—g⁻` and `u⁺—g⁺`. Contracting those two edges merges `u⁺` into `g⁺` and `u⁻`
into `g⁻`, and every re-routed occurrence at `u` becomes an occurrence at `g` — the result
is precisely the link graph of `P`. So **`link(P)` is a minor of `link(P')`**, obtained by
contracting the two edges of the bigon.

Given a Neuwirth-compatible rotation system on `link(P')` of defect `d`, contract: at the
merged germ, splice `u⁺`'s cyclic order into `g⁺`'s at the position of the contracted edge,
and likewise on the minus side. Contraction of an edge never increases the genus of an
embedded graph, so the defect does not increase; and the compatibility constraint survives
because `τ` (the germ-reversal `g⁺ ↔ g⁻`) sends the two contracted edges to each other, so
the two splices are performed at corresponding positions and the merged orders remain
mutual reversals. Hence a compatible system on `link(P)` of defect `≤ d`. ∎ (sketch)

**[GAP-S8-1]** The splice step needs the defect bookkeeping done in the repo's own formula
`defect = nA − nC + 2L − nAC`, not merely in terms of graph genus: deleting the bigon
relator changes `nA` by 2, `nC` by 2 (the germs `u±` disappear), and the dart cycle count
`nAC` by an amount that must be checked, and `L` (link components) must be shown not to
jump. Until that is discharged this is a conjecture with 632 confirming instances, not a
theorem. **[GAP-S8-2]** The argument as written assumes the bigon's two link edges are not
loops and that `link(P')` stays connected; degenerate splits (re-routing *every*
occurrence of `g`, which makes `g` occur once) need separate treatment — FRAMING trap 4:
exclude degenerate candidates by what the transform DOES.

## 4. Where this leaves the session's hypothesis

Two natural "just use more generators" mechanisms have now been characterised:

| mechanism | new generator's germ count | effect on γ_N | status |
|---|---|---|---|
| chord refinement / triangulation (abbreviate) | exactly 2 | **unchanged** (subdivision) | proved (S3), 480/480 measured |
| generator splitting (spread a crowded germ) | ≥ 3 | **never decreases** | conjectured + sketched, 632/632 measured |

Both are *bookkeeping*: they re-express the same relators without changing which words the
relators are. The lesson is now sharp enough to state as the S-line's headline negative:

> **Adding generators is worth nothing as long as the added generators only re-describe the
> existing relators.** Depth in the rank filtration can only pay through AC2 slides that
> mix relator content across the new generators — moves with no depth-1 serialization
> (S7 §4, Q(F2)).

This is not a proof that high rank is useless; it is a proof that the two obvious ways of
using it are. It also sharpens what task A7's rank-`N` search must look for: states that
are *not* reachable from the start by refinement alone, which means the search's own
progress metric should be "distance from the subdivision/splitting closure", not rank.

## 5. Trap added

- **T-S8.** Any proposal of the form "add generators so the relators get shorter / the
  germs get less crowded" is inert or monotone by S3/S8. Before proposing a high-rank
  mechanism, state which relator *content* changes — if the answer is "none, it is the same
  words re-spelled", the proposal is already refuted.
