# Sequential Schreier dictionary: PASS

For the free-group residue map sending axis x to1 modulo d, the dictionary
uses a=x^d and b_(i,g)=x b_(i-1,g) x^-1, starting from b_(0,g)=g for
every old generator other than x. Each local transition satisfies
`x^i * letter = expanded(emitted) * x^j` exactly. Telescoping gives the
full word as emitted subgroup tokens followed by x^j. Choosing a negative
signed residue moves one additional positive a into the subgroup part;
the independent checker verifies this carry and the final free-word identity.

The constructor introduces these helpers one at a time. At every stage the
new definition uses only the current old basis. Future helpers in original-row
templates are recursively expanded until only existing helpers remain. Every
earlier defining row is retained unchanged, and every original row has an
explicit orientation and expansion witness. The audit tracks those labels
through each normalization permutation and checks the final original templates
against the planned full Schreier rewrites.

For old rank r, the number of added helpers is
`H=1+(d-1)(r-1)`. Dictionary rank is r+H; removing one eligible old-axis
relator gives `d(r-1)+1`. The exact dictionary work is
`1+3L+r+H(r+1)+H(H-1)/2` in the stated units. Budget preflight precedes
allocation of the helper inventory, so an enormous requested index can fail
cheaply. This restricts executed work without imposing a fixed rank ceiling.

All six saved planted index2/3/10 chains pass independent replay. The dense
index10 plant uses every planned helper and goes rank2→12→11 with lengths
129→70→64; its dictionary costs465 units. Three corrupt local-transition,
full-image and residue-carry variants are rejected. A sparse10²⁰-label rank3
control reaches rank8, and the enormous-index preflight returns no events at
cost1. The frozen older auditor is preserved; the current sparse defining
checker avoids label-as-rank allocation.

The parent's requested exact U124 check is also saved. Starting from the
pinned current aca0 tuple, index10 on axis1 builds rank12 in132 units and a
single valid removal reaches rank11 at length214. Its full source pointer and
events are in `verification_schreier_aca0_witness.json`. This is a certified
higher-rank detour, not a shortening gain. No census search was rerun.

The finite-index terminology concerns a subgroup of the ambient free group
used to organize the dictionary. The construction is not a claim that the
original trivial presented group has an index-d subgroup. All stable stages
retain the established known-trivial balanced-input hypothesis, and all
relators remain present until the explicitly certified single removal.

Reproduce with `verification_schreier_checks.py`; metrics, source hashes and
the independent real-row validation are in `verification_schreier.json`.
