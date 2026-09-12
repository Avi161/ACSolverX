# Does triangular expansion make difficult AC19 presentations easy?

## Experiment

The hard panel was fixed before running the expanded search. Each of its four
presentations exhausted greedy at 100,000 nodes and later acquired a saved,
replayable solution. Greedy needed 1.5–8.2 million nodes; S20_MK2 needed
17,369–37,682 nodes.

The four S20 rows are pinned in `s20_panel_records.jsonl` (SHA-256
`ee99044b...`), copied from the complete 100,000-node cap-48 campaign at remote
commit `9f50ff3a...`. The greedy records and paths are pinned in
`hard_solved_panel.jsonl`.

Each rank-two pair was expanded by certified defining compressions until every
relator had length three. This raised the rank to 7–9. The subsequent search
used only ordinary AC normal-product substitutions and retained every generator
and relator. No destabilization was permitted. A search counted as solved only
after reaching maximum relator length two and running the exact fixed-rank
terminal compiler to distinct singleton generators.

## Hard-panel result

| ID | Greedy nodes | S20_MK2 nodes | Expanded rank | Cap-5 states, 500 pops | Cap-6 states, 1,000 pops | Unit/bigon/solve |
|---|---:|---:|---:|---:|---:|---:|
| ac19_15866 | 8,204,360 | 17,369 | 8 | 22,910 | 513,781 | 0 / 0 / no |
| ac19_25244 | 1,791,312 | 21,637 | 8 | 20,882 | 520,122 | 0 / 0 / no |
| ac19_44158 | 8,009,273 | 23,977 | 9 | 26,685 | 760,740 | 0 / 0 / no |
| ac19_66724 | 1,506,075 | 37,682 | 7 | 16,507 | 357,084 | 0 / 0 / no |

The complete declared short-macro neighborhood was especially rigid: each
expanded root formed a one-state component. There was no direct triangle
product and no two-substitution route through one quartic relator that returned
to a new all-triangle state.

The cap-6 run examined 4,758,328 rotation products and discovered 2,151,727
distinct generated states in 173.466 search-wall seconds. It generated no unit,
bigon, or terminal. This is a bounded negative search result, not an
obstruction or counterexample.

The cap-5 run took 14.882 wall seconds after moving full determinant replay
from every generated child to retained paths. Its endpoints, paths, pop counts,
state counts, and rotation-product counts exactly match the earlier fully
audited 53.103-second run.

## Positive control

A deterministic twelve-row control panel was selected from AC19 rows solved by
the final rank-two policy in 5–50 units, before observing the expanded outcomes.
The identical triangular expansion and fixed-rank short-macro search solved
5/12. The five solves required 5–8 macro pops. All five terminal forests were
compiled to the retained singleton basis without destabilization. Thus the
negative hard-panel result is not caused by a disabled move or unreachable goal.

## Conclusion

For this test, making every relator length three did not make the difficult
presentations easy. It solved five already easy controls, but all four hard
rows remained at all-triangle endpoints after the wider 1,000-pop search. Each
expanded pop enumerates many relator pairs and rotations, so these pop counts
are not directly comparable with rank-two pop counts. A useful next approach
needs a definition-aware score or macro
that exploits the dependency graph created by the expansion; short relators
alone are not a sufficient guide.

`verify_results.py` independently replays the saved rank-two certificates,
every defining compression, every retained ordinary-AC search event, and every
terminal compiler move. It also checks that rank and the declared generator set
remain fixed after expansion.
