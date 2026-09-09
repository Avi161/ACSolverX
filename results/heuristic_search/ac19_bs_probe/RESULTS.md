# ac19_bs_probe: testing the BS pattern at every state, not just the input

Status: **COMPLETE**, 72,779 / 72,779. Budget 501, cap 255, starter budget 500 --
the shipped screen's own rung, so `cascade501` is the control row for row.
Branch `claude/ac19-leftover-solver-notebook-6yan6d`. Not merged to main.

## The gap

The cascade's stage 2 tests the Baumslag-Solitar pattern **once**, on the
normalized input. That catches a row only if it *arrives* recognizable: 18,839
of 72,779 (25.9%). Nothing tested a row that *becomes* recognizable a few moves
in, and the test is 1/68 of a node (14.9 us against 1,015 us for a pop plus its
~95 children), so the omission was a gap rather than a cost decision.

`cascade_bs` hands the same test to stages 3 and 4 via
`mixed_search(bs_probe=True)`: every popped state is tested, and a match ends
the search by deterministic rewriting. It adds **no moves** -- same AC
substitutions, same four Nielsen images -- only an earlier stopping condition.

## Result

| | `cascade501` | `cascade_bs` | delta |
|---|---:|---:|---:|
| solved | 70,649 | **71,579** | **+930** (+1.32%) |
| **unsolved** | 2,130 | **1,200** | **-43.7%** |
| AC-certified | 27,164 | 27,628 | +464 |
| aut-assisted | 43,485 | 43,951 | +466 |
| nodes explored | 3,214,680 | **2,889,946** | **-10.10%** |
| seconds | 1,966 | 2,083 | **+5.93%** |

**The residue nearly halves.** 2,130 unsolved falls to 1,200 at the same budget.
That is the result; the +1.32% on solves understates it because the denominator
is a screen that was already 97% settled.

**Node budget and wall clock part ways.** Nodes fall 10% while seconds rise 6%.
Anyone buying wall time is paying +5.93% for +1.32% solves; anyone buying a node
budget gets both. Both are quoted because quoting either alone misleads.

## Per-row shape

| | rows | size |
|---|---:|---|
| dearer | 22,381 | median **+1** node, worst +5 |
| cheaper | 4,515 | large -- rows that would have burned the full 501 |
| identical | 45,883 | -- |

A trivial premium on many rows buys a large saving on few. This is the
non-monotonicity in cost, quantified: when the probe costs anything it costs 1
to 5 nodes, because the collapse it runs was dearer than the handful of pops the
plain search still needed.

## Verification

* **0 regressions.** No row solved by `cascade501` is unsolved by `cascade_bs`.
  This is the check that matters: the probe only ever terminates early, the pop
  order is identical until it fires, and a collapse that fires and fails falls
  through unchanged -- so reach cannot fall. Argued first, then measured.
* **`rewrite` winner count identical, 18,839 both sides.** Rows recognizable at
  the input are taken by stage 2 before any search runs, so the probe must not
  touch them, and does not.
* **Bit-identity gate.** `bs_probe=False` through the whole cascade reproduces
  `cascade501` on 200 sampled rows -- same `nodes_explored`, same winner. The
  shipped cascade is unchanged and this is a separate arm.
* 0 rejected certificates. The spliced path (search prefix + collapse tail) is
  replayed by `certify_path` on every substitution-only row.

## What did NOT happen

A collapse path is substitution-only, so I expected the probe to convert
aut-assisted rows into AC-certified ones in bulk. It converts **464** (and 0 the
other way) -- real decoder debt cleared, but small. Meanwhile all **930 new
solves land aut-assisted**, so the aut pile grows by 466 net.

The reason is that the collapse purifies a path only **from the fire onward**.
A prefix that already used an `s40_gen` automorphism stays impure, and those are
exactly the rows deep enough in the search to reach a new BS state. The
certificate mix is set by the prefix, not by how the row finishes.

## Files

| file | what |
|---|---|
| `ac19_cascade_screen_cascade_bs_b501_mrl255.jsonl.gz` | all 72,779 records |
| `unsolved_cascade_bs_b501.csv` | 1,200 rows still open at 501 |
| `aut_assisted_cascade_bs_b501.csv` | 43,951 rows needing the decoder |

Regenerate with
`run_ac19_cascade_screen run --arm cascade_bs --budget 501`.
