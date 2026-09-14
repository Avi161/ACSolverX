# Independent recursive stable-prefix audit

Verdict: **PASS** for the exact report SHA256
`3e6a3d89e652b292051e58cd297abcbf8d29b9bfcceff166d72c8aadc9de0ce2`.

The independent verifier is `recursive_stable_compression_independent_audit.py`;
its machine-readable audit is `recursive_stable_compression_independent_audit.json`.
It exposes `verify_prefix(record)`, returning the shortest verified displayed
boundary with `relators`, `rank`, `total_length`, and `independently_verified`.
The exact previously audited seed provenance is checked on every call.

All85 recursive records replay. Their embedded source table and each exact
source keeper match; all pinned author, convention, prior audit, prior source,
and prior auditor hashes match. Previously independently audited seed checkers
are reused only to verify the old prefixes. The new compression verifier does
not import either recursive compression author module.

For each accepted definition, it independently checks a fresh generator,
a reduced old-alphabet defining word, every cyclic conjugator and cut, the
literal expansion of every compressed word, the retained defining relator,
the enlarged free basis, all balanced-rank boundaries, the all-relator token
count identity, strict length gain, and the final tuple. All accepted inputs
are known trivial-group presentations through their audited MS provenance.
The stable realization uses the finite normal-product lemma in
`STABLE_CERTIFICATE_CONVENTIONS.md`. No normal-product expansion is emitted
or counted as an elementary certificate.

| Input | Rank-three seed total | Rank-four endpoint total | Exact endpoint |
|---|---:|---:|---|
| aca_108 |22|21|UYY, XYxZ, XYZyzxY, Yuuuxuz|
| aca_109 |21|20|UYY, YxxZ, XuZxzy, XXXzuuu|
| aca_111 |22|21|UYY, XZxY, XYxZyzY, UxYuuuZ|
| aca_112 |22|21|UYY, XYxZ, XYZYzxy, UzYuuux|
| aca_113 |21|20|UYY, XXyZ, XzxZY, XXXZuuuu|
| aca_114 |21|20|UYY, XXyZ, XZxYz, uuuuzxxx|

In every case the new defining word is YY, so UYY retains u=y^-2. Four
replaced length-two tokens save four letters at a cost of three for the new
definition: net gain one. All four relators are included in the endpoint
length. The six new reductions total six letters. None is a rank-two endpoint
or a solved presentation.

The separate `aca_24` continuation starts at the independently replayed
canonical total15 seed `(XXZYY,XXyxZ,XYzYZ)`. Its exact source prefix and
endpoint match. Its57 additional candidates produce no further accepted
compression; combined with the old65 candidates this is122 for that input.
The report accounts for9,201 recursive candidates overall, maximum244 for
one input. These accounting fields were checked, but candidate enumeration
completeness and optimality were not independently rerun or certified.

Seven deliberate corruptions are rejected: nonfresh helper, changed compressed
word, invalid cyclic cut, omitted defining relator, changed boundary length,
changed final rank, and altered source provenance. There are no actual
singleton-deletion events in this report; the independent API rejects such
unreviewed paths rather than silently accepting untested generalized logic.
All85 sources and the one continuation pass the exact path audit. No campaign
was rerun. The report's negative scans are finite author observations only;
this pass admits its six explicit positive stable prefixes.
