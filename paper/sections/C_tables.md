# Extended Data Tables {#app:tables}

This appendix collects extended data behind the six numbered tables of the main text (Tables \ref{tab:litchecks}–\ref{tab:floorcensus}) and discusses the three figures that live only in the appendix (\ref{fig:ak3_plateau}, \ref{fig:hard_ties}, \ref{fig:rl_gap}). Every value below is read from the same digest files that produced the main-text tables and figures, and is independently re-derivable from the raw record streams (\ref{app:repro}).

## Extended per-arm statistics

Table \ref{tab:arms} reports median nodes and median path length, over solved presentations only, for the naive $z=w$ stabilization arms. The full min/max/mean/median breakdown, over the same solved-only convention, is:

| Arm | Nodes (min / max / mean / median) | Path length (min / max / mean / median) |
|---|---|---|
| baseline | 3 / 77,385 / 1,662.0 / 11 | 2 / 710 / 32.6 / 8 |
| $r_1$ | 5 / 239,578 / 2,802.6 / 13 | 4 / 714 / 33.8 / 12 |
| $r_2$ | 4 / 291,479 / 3,637.1 / 13 | 3 / 715 / 29.9 / 11 |
| $x$ | 4 / 326,326 / 14,680.7 / 10 | 3 / 102 / 12.1 / 9 |
| $y$ | 4 / 491,437 / 21,832.7 / 10 | 3 / 102 / 11.5 / 9 |

The $x$ and $y$ arms' wide gap between median ($10$) and mean ($14{,}680.7$ / $21{,}832.7$) node counts, set against a comparatively tight path-length distribution (max $102$), is the alias-orbit effect noted in \ref{sec:results}: defining $z$ by an already-present generator does not lengthen solutions, it multiplies equivalent detours the search must exhaust before terminating.

## The 97-word literature-grounded bank

Table \ref{tab:wordbank} gives family sizes. The full bank — 95 words across seven families, plus the two per-target control words $z=r_1,r_2$ added at run time to reach 97 — grouped by family in escalation-priority order, is:

**relhalf** (17): xyx, yxy, xxx, yyyy, yxx, xxy, xyy, yyx, XYX, YXY, XXX, YYYY, xyxY, Yxyx, xx, yy, yyy

**wk** (17): yyyyyyyyXyxy, yyyyyyyXyxy, yyyyyyXyxy, yyyyyXyxy, yyyyXyxy, yyyXyxy, yyXyxy, yXyxy, Xyxy, YXyxy, YYXyxy, YYYXyxy, YYYYXyxy, YYYYYXyxy, YYYYYYXyxy, YYYYYYYXyxy, YYYYYYYYXyxy

**wstar** (5): YxyX, XyxY, xYXy, yXYx, xYxY

**conj** (14): x, xyX, yxY, y, Xyx, Yxy, xyxYX, yxyXY, xYxyX, YxyXy, xxyXX, yyxYY, XYxyx, XyxYx

**comm** (6): XYxy, YXyx, xyXY, yxYX, XyXy, xyXYX

**ms** (3): Xyxyy, yxyx, xyxyy

**brute** (33): X, Y, xy, xY, XX, Xy, XY, yx, yX, Yx, YX, YY, xxY, xYx, xYX, xYY, XXy, XXY, XyX, Xyy, XYx, XYY, yXX, yXy, yXY, yyX, Yxx, YxY, YXX, YXy, YYx, YYX, YYY

Each name is the induced word $w$ in $x^{\pm1},y^{\pm1}$ under the encoding of \ref{app:glossary} (capital letter = inverse); each induces a $z$-relator $z\cdot w^{-1}$, deduplicated by that induced relator and dropped if it violates the per-relator cap $L=24$.

## Campaign facet breakdown

Lane D's $16{,}870$ solve attempts (Table \ref{tab:lanes}) are drawn from four resumable facets, every one contributing $0$ solved: D1 ($5{,}866$ solve attempts), D2 ($5{,}350$), D3 ($5{,}497$), and a resolve pass at the raised per-relator cap $L=40$ ($157$ solve attempts, probing whether the $L=24$ cap specifically — as opposed to the total-length cap — was pruning a viable descent among the shortest candidates). The four facets sum to the reported $16{,}870$; $0$ of $16{,}870$ solve attempts succeed across all four.

## Floor census detail

The two canonical (signed-relabel) representatives of the length-13 floor of AK(3)'s AC-class (Table \ref{tab:floorcensus}) have relators, under the encoding $x\!\to\!1,\ X\!\to\!-1,\ y\!\to\!2,\ Y\!\to\!-2$:

- $F$ — a 2-generator presentation AC-equivalent to AK(3): `YYxyXX` / `YYYXXyx`, i.e. $y^{-2}xyx^{-2}$ and $y^{-3}x^{-2}yx$ — the dominant attractor, $712/1006$ ($70.8\%$).
- AK(3)'s own reduced form: `YXYxyx` / `YYYxxxx` — $294/1006$ ($29.2\%$).

Each census candidate is assigned by canonicalizing its terminal state and checking equality with one of these two representatives up to signed relabeling (\ref{app:glossary}); no third representative appears anywhere in the 1,006-candidate census.

## Grid-probe list

Beyond Lane D's harvested-quotient attempts, the campaign ran $14$ additional grid probes (Table \ref{tab:lanes}, Lanes A–C):

| Lane | Probe | Nodes | Floor |
|---|---|---|---|
| A (MITM) | from AK(3), against 1,177 targets | 2,000,000 | 13 |
| A (MITM) | from P25, against 1,177 targets | 2,000,000 | 13 |
| B (StableSolver) | hero-8 bank, $g\le3$, gen-penalty 2, from P25 | 800,000 | 13 |
| B (StableSolver) | hero-8 bank, $g\le3$, gen-penalty 2, from AK(3) | 800,000 | 13 |
| B (StableSolver) | hero-8 bank, $g\le3$, gen-penalty 1, from AK(3) | 800,000 | 13 |
| B (StableSolver) | hero-8 bank, $g\le4$, gen-penalty 2, from AK(3) | 800,000 | 13 |
| B (StableSolver) | full 95-word bank, $g\le3$, from AK(3) | 300,000 | 13 |
| B (StableSolver) | full 95-word bank, $g\le3$, from P25 | 300,000 | 13 |
| C (trivial-$z$) | rep form, $n=3$ | 1,500,000 | 14 |
| C (trivial-$z$) | textbook form, $n=3$ | 2,000,000 | 14 |
| C (trivial-$z$) | rep form, $n=4$ | 1,000,000 | 15 |
| C (trivial-$z$) | textbook form, $n=4$ | 1,500,000 | 15 |
| C (trivial-$z$) | rep form, $n=5$ | 800,000 | 16 |
| C (trivial-$z$) | textbook form, $n=5$ | 1,000,000 | 16 |

All 14 probes floor within their searched budgets; $0$ of 14 solve.

## Discussion of the appendix figures

**Figure \ref{fig:ak3_plateau}.** At $10^5$ nodes the representative form's floor histogram is already concentrated ($79$ words at floor $13$, $11$ at $14$, $7$ at $15$); escalating every unsolved word tenfold to $10^6$ nodes tightens the concentration further ($88/2/7$) rather than dislodging any word past the floor, and the textbook form shows the identical pattern ($77/11/9$ at $10^5$, sharpening to $86/2/9$ at $10^6$). Every one of the $97\times2\times2=388$ solve attempts across both forms and both budgets records $0$ solved, within the searched budgets, against a trivial target of total length $3$; more nodes concentrate the distribution on the floor rather than escaping it, evidence that the obstruction is structural rather than a matter of search depth.

**Figure \ref{fig:hard_ties}.** On the two hard-but-solvable controls, the floor histograms sit far above AK(3)'s own (index $625$: range $17$–$25$, peaking at $19$ with $41$ of $98$ words; index $610$: range $16$–$23$, peaking at $19$ with $34$ of $99$ words), confirming these are genuinely different, easier landscapes with their own internal spread. Yet the only words that solve are, in both cases, exactly the target's own relators and their relator-derived `relhalf` twins, and they solve at identical node counts (index $625$: $r_1$ and its `relhalf` twin both at $77{,}395$ nodes; $r_2$ and its twin both at $80{,}111$; index $610$: $r_1$ and its twin both at $61{,}082$) — the same search in disguise, not a shortcut. Within the searched $10^5$-node screen (the specified $10^6$-node full tier was not run on these generic-family words), no structurally distinct word ever solves either target.

**Figure \ref{fig:rl_gap}.** The pretrained policy's own training-distribution path lengths are short and tightly clustered (mean $6.1$, range $2$–$16$, mode at length $4$: $31$ of $155$ items), and it solves all $155$ of $155$ solve attempts on that distribution. Run zero-shot on the $155$ floor and stabilized states at beam width $512$, $0$ of $155$ solve attempts succeed; widening to beam width $2048$ with temperature annealing on the hardest $30$-state core, $0$ of $30$ solve attempts succeed. Within these two beam-search configurations, the size of this gap — perfect in-distribution, zero out-of-distribution, on states sharing the same 2-generator alphabet the policy was trained on — is the sharpest illustration in the campaign that the floor resists every method family tried, learned or hand-designed, within the budgets searched.
