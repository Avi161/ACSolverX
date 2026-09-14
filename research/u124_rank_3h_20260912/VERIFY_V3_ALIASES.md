# Neutral helper-alias preference audit: PASS

Version3 changes the dictionary weight to `(token length,old-token count)`.
The pair is additive, nonnegative, well founded and translation invariant;
the audited saturation and exact-target dynamic-programming proof therefore
applies unchanged. It selects a helper-rich spelling among equal shortest
token lengths, while retaining length as the primary objective.

An independent tiny control sets h=a b a^-1. The target a b has the neutral
alias h a, with equal length2 and only one old token. Seventeen exact reduced
targets of length at most2 agree with exhaustive signed-token alternatives.
For these queries, longer alternatives cannot improve the primary objective,
so the enumeration covers every potential better or tied candidate.

Full defining-template events on the known-trivial commutator plant pass
independent native/JSON word expansion, retained-row, normalization and cost
checks at budgets40 and1000. A repeated zero-budget saturation correctly
clears the completion claim. `verify.py` now recognizes the new method and
checks its objective metadata without expecting obsolete graph fields.

Completion concerns the selected exact orientation and fixed dictionary only.
Orientation selection, definition planning and bounded query prefixes remain
separate restrictions. Partial fallback templates are valid witnesses with
incomplete status. No global presentation minimum or new census gain follows
from the weighting change alone.

No bug was found. Reproduce with `verification_v3_checks.py`; results and
source hashes are in `verification_v3_aliases.json`. No census search was run.
