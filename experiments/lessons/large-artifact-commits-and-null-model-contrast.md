# Large result artifacts: GitHub's 100 MB limit; and matched-operator contrast design

2026-07-29, fable line, R3′ battery/control arc.

- [TRAP] GitHub rejects any file > 100 MB at push time (pre-receive hook), even when
  the local commit succeeds — a 124k-row harvest jsonl with per-row replay provenance
  hit 101.43 MB and bounced the whole push. Fix that keeps everything on the branch:
  commit the artifact gzipped (3.2 MB at level 9 for repetitive jsonl — 30×) and give
  the session-created test fixture a transparent `.gz` fallback (plain file takes
  precedence when regenerated locally). Amend the unpushed commit; never leave the
  plain file tracked.
- [TRAP] Harvest-operator choice dominates calibration conclusions: the exact-key
  AK(2) control (0/1,251 spherical) and the rotation-expanded AK(2) control (397/13,040
  spherical, 227 non-degenerate) describe THE SAME CLASS at the same pop budget. Never
  compare hit rates across harvests with different operators; a contrast experiment
  must verify operator identity member-by-member on the harvest layer (the AK(3)
  control did, recorded in its summary).
- [WORKS] Two-sided null-model accounting: report ΣE and observed hits for BOTH the
  open-class run and a provably-trivializable positive control under the identical
  operator; calibrate the open-class expectation by the control's observed/expected
  factor and report both raw and calibrated p. (AK(3): ΣE 5.03, 0 observed, p 0.65%
  raw / 4.6% calibrated — recorded as tension, not phenomenon; the scale tier decides.)
