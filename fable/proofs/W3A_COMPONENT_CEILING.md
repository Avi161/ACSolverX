# W3a: ceiling 17 is the largest locally-closable AC-component ceiling

Date: 2026-08-28 · Checker: `checkers/ak3_component_ceiling_probe.py`
(schema `ak3-component-ceiling-probe-v1`; guarded run).

Independent re-implementation of the AK(3) component BFS (full
Definition-2.1 move set via `acmoves.children`, per-relator cap =
ceiling − 1, canonical states, closure replay):

| ceiling | cap | verdict | states |
|---:|---:|---|---:|
| 17 | 16 | **CLOSED** (closure replay passed) | 1,000 |
| 18 | 17 | **EXCEEDS** the 1,000-pop law | ≥ 1,243 at cutoff |

- The ceiling-17 result exactly reproduces the certified
  `ak3-component-thickenability-v1` state count from an independent
  driver — a cross-validation of that certificate.
- The ceiling-18 component is strictly larger than the local budget
  allows; per the advisor-review principle, a truncated BFS is a sample,
  not a frontier, so no partial scan is reported.
- Production handoff (user-run, Colab): close ceilings 18–20 with the same
  driver at a raised pop budget, then run the certified 7-family planarity
  dispatch (`two_hop_cov_thickenability_certificate._dispatch` chain) over
  the new states; any SPHERICAL hit is quarantined per the Pipeline-B
  doctrine and would, validated, prove AK(3) **unstably** AC-trivial
  (states here are classical rank-2 AC moves from AK(3)).

No thickenability, AK(3), stable AC, or AC claim is made here.
