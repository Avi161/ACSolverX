# EXP-25 — the same ordering from all eight relabels, at full budget each

Decidable band (bins 4–7, 24 rows), budget 1000 **each**, cap 48. A relabel renames the generators: same AC-class, same orbit invariants, *different string* — and the greedy reads strings. This is the combination EXP-17 (divided budget), EXP-12 (no dynamic range) and EXP-21 (varied the ordering, not the string) each left untested.

| ordering | identity relabel only | any of the 8 | gain | rows added |
|---|---|---|---|---|
| recommended | 19/24 | **19**/24 | **+0** | — |
| baseline (length) | 5/24 | **5**/24 | **+0** | — |

## Verdict

Relabels add **nothing** at full budget on this tier: 19/24 from all eight against 19/24 from the identity alone. The repo's 14-of-17 flip result came from a different setting (one-hop CoV starts at a smaller budget), and it does not transfer to the tuned ordering here — this ordering appears insensitive to how the presentation is written, which is a mildly reassuring property in itself.

## Which relabel solves, when the identity does not

| ordering | row | relabel that solved it | nodes |
|---|---|---|---|
| — | — | — | — |

## The arm can move — so the negative is real, and it has a mechanism

A zero gain is only meaningful if the eight searches were genuinely different. They were, but barely: **19 of the 24 rows show more than one distinct node count across their relabels**, so the searches do diverge — yet the spread is tiny. `ms538` runs 517, 518, 518, 519, 529, 530 nodes; `ms565` runs 419–423. These are perturbations of one search, not eight different ones.

That is the explanation, and it is a property of the solver rather than of the presentations. Every state is canonicalised before it enters the heap — `canonical_pair_nj` applies Booth lex-minimal rotation and orders the pair — and a signed-permutation relabel is very nearly *inside* the group that canonicalisation already quotients out. So renaming the generators mostly produces the same canonical states in the same order, with a handful of tie-breaks landing differently. Whatever the string looked like on the way in, the search is walking almost the same graph.

This also retro-explains EXP-17: when a divided budget's alternate relabels "almost never fired", that was not bad luck about which restart got lucky — the alternates were re-running nearly the same search on a shorter budget.

**A tension worth stating rather than smoothing over.** The repo records relabels supplying 14 of 17 unsolved→solved flips in the one-hop CoV sweep, which is the opposite of what happens here. The two settings are not the same: that sweep applied relabels to *change-of-variables transformed* presentations — states produced by substituting a word for a generator, which genuinely leave the canonical orbit — whereas this applies them to the original presentation, where canonicalisation absorbs them. The safe reading is that a relabel is worth something when composed with a transform that has already moved the presentation, and worth nothing on its own. This experiment establishes the second half only.

**Practical consequence:** do not spend 8× compute on relabels of the same presentation. Spend it on a structurally different *ordering* (EXP-21/22), which does pay.
