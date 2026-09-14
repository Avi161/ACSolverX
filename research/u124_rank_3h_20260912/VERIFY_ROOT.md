# Root-derived forced template audit: PASS

For an oriented old relator R and old-generator contexts U,V, suppose
H=red(R V^-1 U)=g^p with integer p≥2. Set w=red(g U^-1). Then

`R = (w U)^(p-1) w V`

as an exact free-group identity. A new helper h=w therefore gives the exact
template `(h U)^(p-1) h V`. If inverse deduplication chooses w^-1 instead,
the helper token must be negative; the independent checker verifies this sign.
It also checks the original orientation conjugator, root power, contexts,
definition, forced row, all retained relators, normalization, helper counts,
isolatable-generator metadata and the additional expansion charge.

Root extraction first writes a nonempty reduced word as t C t^-1 with C
cyclically reduced. It then finds the primitive literal period of C and
enumerates all divisors of its repetition count. This covers every positive
integer power decomposition of that fixed word. The independent audit uses a
separate direct period-divisor oracle and checks 238 words, including conjugated
powers and nonpowers. Every reported root is multiplied back independently.

The commutator plant `(abbAB,aabAB)` gives a complete valid event. Its input is
known trivial independently: c=[a,b] gives cbc=1 and ac=1, hence c=a^-1,
b=a² and c=[a,a²]=1. The same event construction works after adjoining nine
singleton generators, taking rank11 to rank12 with generator IDs above10²⁰.
Five corrupted root metadata variants are rejected. Small budgets0,1,5,17,40
stay within their declared work limits.

The root extraction for a fixed word is complete, but context, orientation,
plan and downstream removal exploration are bounded. This is an exact
sufficient template constructor, not a complete stable-AC search. Its stable
legality retains the known-trivial balanced-presentation hypothesis; this
audit does not replace it with an abelianization test or claim an expanded
elementary move list.

No algebraic bug was found. Reproduce with `verification_root_checks.py`;
`verification_root.json` stores the checked event, metrics and source hashes.

The separate `verification_templates_gain95.json` independently anchors and
replays the saved aca95 path: saved-rank2 length19 → template rank3 length18
→ Whitehead rank3 length17. The new gain against the pinned length18 baseline
is exactly one. No census search was rerun for either audit.
