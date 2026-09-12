# Independent ordinary AC audit after stable dictionary compression

**PASS.** `aca_24` has a further certified rank-three reduction: its original pair has total length **17**, the audited dictionary tuple has total **16**, and the explicit ordinary AC suffix reaches

`(XXZYY, XXyxZ, XYzYZ)`, total **15**.

All three relators are retained and counted. The ordinary suffix minimum, including every temporary donor and every elementary intermediate state, is also 15. No rank-two endpoint or solve is claimed.

The source definition is `w=YYXX`, with cuts `(4,6)` and exact compressed tuple `(ZYYXX,XYxxz,XYxYzY)`. Its literal expansion is rechecked with the independent dictionary auditor. The initial signed conjugations produce `(XXZYY,XXyxZ,XYxYzY)`. The only accepted substitution targets row 2 with row 1 as a positive donor. Rotating that donor after its first four letters gives `ZXXyx`; multiplication produces the exact raw target `XYxYzYZXXyx`. The donor is restored before the saved target canonicalization, whose conjugator is `XYxYzYZ`, producing `XYzYZ`.

The auditor expands initial inversions/conjugations, target and donor cuts, multiplication, donor restoration and final canonicalization into strict AC1/AC2/AC3 moves. Its integer stack replay and a separate repeated-adjacent-cancellation string replay agree at **every state**. For `aca_24` the ordinary suffix has **21 elementary moves**, including initial normalization, and the first minimum occurs after move 17. The stable definition preceding this explicit suffix remains a theorem-backed macro; its finite normal-product expansion is not emitted.

All 84 saved rank-three suffix records, including the 83 with no accepted substitution, were independently replayed. Their source words match the pinned dictionary records. The audit does not rerun the negative local-minimality enumeration. The source's corrected field `locally_minimal_endpoint_rows=84` describes final endpoints; it is compatible with `aca_24` improving before its final failed descent sweep.

The source logged 36,328 substitution child evaluations, at most 640 per row. Adding each row's preceding dictionary-definition candidate count gives a maximum **813** declared work units per original input; `aca_24` uses **742**. These units do not count the unexpanded stable normal-product path or every cyclic-tokenization dynamic-program operation. Four corruptions of the saved substitution (sign, donor cut, boolean target cut, raw product) are rejected. Audit runtime was 0.0088 CPU seconds.

## Adapter API and provenance

`stable_rank3_ac_independent_audit.py` exposes `verify_prefix(record)`, where `record` is a row of `stable_rank3_ac_descent_report.json`. It returns the complete minimum boundary with `relators`, `rank`, `total_length`, `relator_lengths`, and `independently_verified: true`, together with the exact elementary suffix, all replayed rank-three boundaries, endpoint and minimum move index. The ledger retains the source JSON pointer and exact input for every row.

Source report SHA-256: `887e960e3a578c8f81fd5a6d0996aae80c11575228f016c5cef3c7cf7f068bb1`. Auditor SHA-256: `fb35cbed1f29ea1c1e7caaefff86c69a3af7f489e3870e9cb5e8380561ebf6aa`. The original executed author SHA and current reporting-only author SHA are both retained because the source renamed one summary field without rerunning words or timings. The dictionary report, independent dictionary auditor and original best-input CSV are separately pinned.
