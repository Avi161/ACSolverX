# Partial-basis extraction

`partial_basis.probe(words, remaining)` returns `(candidates, charged)`, with
each candidate `(after, events)`. Words are tuples of arbitrary nonzero signed
integer generator IDs. Survivors keep their original IDs. `remaining` must
be an integer in `0..1000`; there is no rank or length ceiling.

The caller must establish that the input is a balanced presentation of the
trivial group. The returned paths are theorem-backed stable composites under
Lemma11, with exact word and basis-map witnesses. They are not fully expanded
elementary AC certificates, and the API does not label a result solved.

## Search performed

At rank three and above, each pair of relators is a possible selected
subtuple. At ranks two through five, the plans also include subtuples of size
`rank-1`; duplicate selections are removed. Plans are ordered by selected
length minus selected cardinality, then decreasing cardinality and row IDs.
Each starts from the normalized input. The remaining work allowance is shared
among the remaining plans, with unused work carried forward.

For each plan, the existing minimum-cut routine builds its Whitehead graph
from the **selected subtuple**. Every accepted map strictly lowers the selected
sum, and the recorded map and checked inverse are applied to **all** relators.
The whole presentation is allowed to increase in length. A partial final cut
scan can still supply a valid improving map; its event records that the scan
was incomplete.

`lemma11.normalize_witness` determines every canonical row permutation. The
selected indices are transported using each row's `input_index`, including
ties between equal words. After removals, the mapping composes the surviving
original row IDs with the removal's normalization permutation.

Two sufficient gates are used:

- If the selected words become distinct signed one-letter relators, remove
  them successively with `lemma11.remove_one`. The event records whether the
  entire selected group was removed before the budget ran out.
- Otherwise, at the exposure endpoint, each exact one-occurrence generator
  in a selected relator supplies a separate Lemma11 removal candidate. This
  gate does not assert that the selected subtuple is a free-basis subset.

Each removal candidate then uses its remaining allocation for the existing
whole-tuple `whitehead.descend`. No primitive assertion is inferred from an
exponent vector, determinant, or a failure to find a decreasing cut. Only
candidates containing an actual removal are returned. Equal endpoints are
deduplicated after evaluation, retaining a shorter event list; their failed
and duplicate work remains charged.

## Accounting and event fields

Every actual minimum-cut evaluation and every `remove_one` evaluation costs
one unit, including cuts that find no descent. Normalization, map replay, and
candidate bookkeeping are not separate units. These heterogeneous work units
are not elementary moves or an estimate of normal-product expansion size.

The returned `charged` is the total work across all plans and branches. A
particular returned path omits failed alternatives and therefore does not
encode the total charge by its event count. Failed cleanup cuts are retained
in the preceding removal's `cleanup_cut_evaluations` metadata.

The ordinary event kinds are preserved: `relator_normalization`,
`ambient_whitehead`, and `lemma11_removal`. Extra metadata includes the
selected indices before/after a map or removal, selected and whole length
changes, cut-scan completeness, the exact removal gate, and whole-tuple
cleanup completion.

## Verified planted control

The sparse-ID input is

`((11,29), (29,47), (11,11,11,-47,-47,-47,29))`.

Writing these generators as `x,y,z`, the first two relators give `x=y^-1`
and `z=y^-1`; the third, `x^3 z^-3 y`, becomes `y`. Thus this is a known
trivial presentation, independent of its abelianization.

With allowance100, the probe uses55 units and returns five distinct
candidates. Its best candidate is `((-29,),)`, rank one and length one. Its
selected-pair Whitehead step lowers the selected sum by two while raising
the whole sum by two. Normalization moves the selected row indices from
`(1,2)` to `(0,2)`; both exposed singleton donors are then removed. This
exercises the intended behavior that whole-tuple length descent can reject.

An instrumented validation intercepted **every** call to
`whitehead.minimum_cut` and `lemma11.remove_one`, and the sum equaled the
reported charge for every control:

| Rank | Allowance | Charged | Distinct candidates |
|---:|---:|---:|---:|
| 3 | 0 | 0 | 0 |
| 3 | 1 | 1 | 1 |
| 3 | 2 | 2 | 2 |
| 3 | 9 | 9 | 2 |
| 3 | 23 | 23 | 3 |
| 3 | 100 | 55 | 5 |
| 4 | 150 | 150 | 9 |
| 11 | 80 | 80 | 29 |
| 2 | 50 | 9 | 1 |

The rank-four control was `((1,2),(2,3),(3,4),(4,))` and exercised selected
triples. The rank-eleven control used singleton relators on IDs101 through111.
The rank-two control was `(xxyXY,xy)` from the nonprimitive-unit-exponent
example in `THEOREM_NOTE.md`; every emitted gate was checked from actual
letter occurrences.

All candidate event lists were JSON-round-tripped and replayed. The validator
independently expanded the ambient maps, checked both inverse compositions,
replayed conjugation/inversion normalization witnesses, reconstructed selected
row IDs, and called the independent removal decoder. Invalid budgets
`-1,1001,True,1.5` and a Boolean letter were rejected. No census row was run.

Verified source SHA-256 values:

- `partial_basis.py`: `4886eeefa49b68c2885bb462172a1f02341efafc45ccf48fadbc22c41610bc39`
- `lemma11.py`: `177bcfc4939e9de0c6fae574edcb13ce9a82e9a33e8dc1022a7b15882166fe1f`
- `whitehead.py`: `d24abe85a4d3abf2920c567f264f79122ec32c8440ab3c300dcca7a0c1dfb928`
- `search.py`: `ad1d911988adf9fe31e4283ff82de5ea36bd1c8085d925ef9e8cf5e0c5339a9e`
