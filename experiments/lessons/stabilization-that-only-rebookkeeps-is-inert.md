# Extra generators are worthless while they only re-describe the same relators

**Filed 2026-08-04, S-line (`claude/stable-ac-conjecture-stabilization-rwo9as`).**
Cost: the first hour of a session was spent building, and then having to kill, a route that
a one-line topological observation refutes.

## The trap

"Hard presentations might get easier with more generators" is a natural and appealing
hypothesis. The two obvious ways to cash it in are:

1. **Abbreviate** — introduce `z = w` and replace occurrences of `w`, shortening the
   relators (triangulation, straight-line-program compression, Lackenby's Lemma 3.1 shape);
2. **Split** — introduce a copy `u = g` and re-route some occurrences of a crowded
   generator onto it, thinning the link graph's high-degree germs.

Both are **provably or measurably inert for thickenability**:

- **Abbreviation is a subdivision.** The new 1-cell is a *chord drawn inside an existing
  2-cell*: `|K_{P'}| ≅ |K_P|`, the same space with a finer cell structure. Not only is the
  γ_N = 0 predicate preserved — the entire defect histogram is bit-identical (1,525
  triangulations, zero deviations). AK(3) sits at `minimum_defect` 4 at rank 2 *and* at
  rank 9, and its census size is literally unchanged (86,400 both), because a peel only
  relocates letters and never changes an original germ's degree.
- **Splitting is monotone.** `link(P)` is a **minor** of `link(P')` — contract the two link
  edges the length-2 definition relator contributes — so genus cannot fall: 632 split
  states across ranks 4 and 6, not one below its base.

## The rule this leaves

> Before proposing any high-rank mechanism, say **how many 2-cell germs the new edge
> carries**. Exactly two germs *from two distinct 2-cells* ⇒ the refinement is a
> subdivision and provably cannot help. Anything that is "the same relators, re-spelled" is
> already refuted; only moves that change relator **content** can change γ_N.

The dividing line is the germ count, **not** the occurrence count: a new generator used
twice *inside one relator* glues a cell to itself and is not a subdivision
(`("zxZy","xxy")` has defect 2 while `("xy","xxy")` has defect 0).

## The corollary that is actually useful

The same theorem read forwards makes subdivision a **free re-coordinatization**: because it
preserves the whole census, you may move a presentation to any rank you like for
*presentational* convenience without perturbing any Neuwirth measurement. And because
splitting bounds γ_N from **above**, a defect-0 verdict computed after splitting is a valid
certificate for the base — while a positive verdict after splitting proves nothing about it.
Record which side of the bound each instrument sits on before reading it (see
`parallel-runs-and-bound-direction.md`).

## Units, while we are here

`gamma_N_factorial_n` returns `minimum_defect`; this project's **γ_N is
`minimum_defect // 2`**. Comparing one against the other manufactures a factor-2 anomaly
and invites a wrong theory to explain it. That happened in this session: a "γ_N went 2 → 4
under triangulation" line was written, and a whole trap ("only the predicate is invariant,
not the value") was filed on the strength of it, before the units were checked. Both were
wrong; the value is invariant.
