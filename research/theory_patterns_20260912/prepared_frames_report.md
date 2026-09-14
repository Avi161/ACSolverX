# Prepared ordinary AC frames

The fixed 124-row screen found **0 solves and 0 strict total-length improvements** over the authoritative saved best inputs.

The portfolio is finite: x/y columns, literal/minimum-span cyclic orientations, left/right signed row products, and target 0/1 tie resolution (16 preparation branches maximum). Each distinct prepared frame tries lower-first and upper-first boundary orders. It uses no ambient automorphism, stabilization, heap, JIT, or saved baseline rerun. Minimum-span orientation scores every literal cyclic rotation and emits its prefix conjugation explicitly. Both relators are cyclically reduced by explicit conjugations before preparation; each updated target is similarly reduced after a row product.

For a column (a,b) with both entries nonzero, choose a target with larger absolute value (the fixed target breaks equality). Replace that relator by its signed product with the other, choosing the sign that subtracts the smaller absolute entry. The resulting absolute target entry is |a|-|b| (with roles exchanged if necessary), so |a|+|b| strictly decreases by the smaller positive absolute entry. Elementary row operations preserve gcd, hence primitive columns terminate at (±1,0) in one of the two relator orders. The compiler receives the actual source index; no relator swap or basis change is implicit. Left multiplication A←B^s A is emitted as A←A^-1, A←A B^-s, A←A^-1, with donor inversion restored inside the signed right multiplication.

All branches start from the original saved-best pair. Framing recognizes a column for one charge, scores each orientation candidate for one, charges one per whole-word orientation/cleanup conjugation, and charges every inversion or multiplication used for signed row products. Each Euclidean step has a separate recognition charge. Preparation is capped at 128 charges per branch and each theorem call at 128, all deducted from one shared limit of 1,000 per input. Duplicates are detected only after paid preparation and avoid repeated theorem calls. Discarded resource-limited staged operations remain charged. Emitted generator-level certificate length is recorded separately. Validation, certificate emission/replay and output costs are outside algebraic charges and inside wall/CPU measurements.

The completed run had zero intentional cooldown: the request for per-row cooling arrived after it launched. The runner now defaults to 0.2s between fresh rows and records that time separately; this code-only addition was tested on a toy cohort without rerunning U124. Its exact pre-edit executed source is preserved in the JSON report.

The preselected20 was run and verified first. Full124 reuses those records and evaluates only the remaining104. These retained bounded AC/Aut components are an upper bound, not124 proved distinct AC classes. The20-row structural panel is a development diagnostic, not a representative validation sample.

Checks: 824 planted/edge cases; every preparation final/best path and every composed theorem final/best path independently replays. Sources are pinned by SHA-256 in `prepared_frames_report.json`.

| cohort | solved | strict length gains | framing charges | theorem charges | total charges | algorithm wall s | algorithm CPU s |
|---|---:|---:|---:|---:|---:|---:|---:|
| panel (20) | 0 | 0 | 6316 | 8963 | 15279 | 8.068722 | 8.056344 |
| full_u124 (124) | 0 | 0 | 33526 | 67150 | 100676 | 43.824544 | 43.759391 |

Maximum per-input work: 1000; theorem calls: 2432; completed stable-boundary passes: 4315; completed extreme-power passes: 628; largest composed certificate: 11992 elementary moves.

A completed span-decreasing pass is an algebraic rewrite result; it is not an ordinary total-length gain. Every branch records its exact final pair, best prefix pair, initial potential, final spans, failed checkpoint and composed ordinary certificate. Best-prefix total length is compared directly with the authoritative saved-best original, separately from the archival initial input.

The theorem reason counts are `{"certificate_limit": 46, "criterion_failed": 2133, "indexed_word_limit": 64, "word_limit": 93, "work_limit": 96}`.

| row | solved | archival initial | starting best | new best | charges | best elementary moves |
|---|---:|---:|---:|---:|---:|---:|
| aca_0 | false | 18 | 18 | 18 | 1000 | 0 |
| aca_1 | false | 15 | 15 | 15 | 495 | 0 |
| aca_2 | false | 16 | 16 | 16 | 544 | 0 |
| aca_3 | false | 17 | 17 | 17 | 1000 | 0 |
| aca_4 | false | 18 | 18 | 18 | 676 | 0 |
| aca_5 | false | 19 | 19 | 19 | 1000 | 0 |
| aca_6 | false | 19 | 19 | 19 | 893 | 0 |
| aca_7 | false | 16 | 16 | 16 | 1000 | 0 |
| aca_8 | false | 15 | 15 | 15 | 454 | 0 |
| aca_9 | false | 15 | 15 | 15 | 516 | 0 |
| aca_10 | false | 15 | 15 | 15 | 538 | 0 |
| aca_11 | false | 15 | 15 | 15 | 472 | 0 |
| aca_12 | false | 15 | 15 | 15 | 498 | 0 |
| aca_13 | false | 16 | 16 | 16 | 615 | 0 |
| aca_14 | false | 15 | 15 | 15 | 744 | 0 |
| aca_15 | false | 17 | 17 | 17 | 591 | 0 |
| aca_16 | false | 17 | 17 | 17 | 608 | 0 |
| aca_17 | false | 17 | 17 | 17 | 575 | 0 |
| aca_18 | false | 17 | 17 | 17 | 786 | 0 |
| aca_19 | false | 17 | 17 | 17 | 590 | 0 |
| aca_20 | false | 17 | 17 | 17 | 612 | 0 |
| aca_21 | false | 17 | 17 | 17 | 663 | 0 |
| aca_22 | false | 17 | 17 | 17 | 689 | 0 |
| aca_23 | false | 17 | 17 | 17 | 638 | 0 |
| aca_24 | false | 17 | 17 | 17 | 728 | 0 |
| aca_25 | false | 17 | 17 | 17 | 680 | 0 |
| aca_26 | false | 17 | 17 | 17 | 600 | 0 |
| aca_27 | false | 17 | 17 | 17 | 598 | 0 |
| aca_28 | false | 17 | 17 | 17 | 566 | 0 |
| aca_29 | false | 17 | 17 | 17 | 1000 | 0 |
| aca_30 | false | 17 | 17 | 17 | 1000 | 0 |
| aca_31 | false | 17 | 17 | 17 | 709 | 0 |
| aca_32 | false | 17 | 17 | 17 | 867 | 0 |
| aca_33 | false | 17 | 17 | 17 | 528 | 0 |
| aca_34 | false | 18 | 16 | 16 | 677 | 0 |
| aca_35 | false | 18 | 18 | 18 | 722 | 0 |
| aca_36 | false | 18 | 16 | 16 | 1000 | 0 |
| aca_37 | false | 19 | 19 | 19 | 553 | 0 |
| aca_38 | false | 19 | 19 | 19 | 618 | 0 |
| aca_39 | false | 19 | 19 | 19 | 591 | 0 |
| aca_40 | false | 19 | 19 | 19 | 1000 | 0 |
| aca_41 | false | 19 | 19 | 19 | 950 | 0 |
| aca_42 | false | 19 | 19 | 19 | 966 | 0 |
| aca_43 | false | 19 | 18 | 18 | 254 | 0 |
| aca_44 | false | 19 | 18 | 18 | 749 | 0 |
| aca_45 | false | 19 | 19 | 19 | 894 | 0 |
| aca_46 | false | 19 | 19 | 19 | 856 | 0 |
| aca_47 | false | 19 | 19 | 19 | 979 | 0 |
| aca_48 | false | 19 | 19 | 19 | 710 | 0 |
| aca_49 | false | 19 | 19 | 19 | 999 | 0 |
| aca_50 | false | 19 | 19 | 19 | 916 | 0 |
| aca_51 | false | 19 | 19 | 19 | 582 | 0 |
| aca_52 | false | 19 | 19 | 19 | 855 | 0 |
| aca_53 | false | 18 | 18 | 18 | 882 | 0 |
| aca_54 | false | 19 | 19 | 19 | 736 | 0 |
| aca_55 | false | 19 | 18 | 18 | 528 | 0 |
| aca_56 | false | 19 | 19 | 19 | 974 | 0 |
| aca_57 | false | 19 | 19 | 19 | 1000 | 0 |
| aca_58 | false | 20 | 17 | 17 | 1000 | 0 |
| aca_59 | false | 20 | 20 | 20 | 988 | 0 |
| aca_60 | false | 20 | 20 | 20 | 990 | 0 |
| aca_61 | false | 20 | 20 | 20 | 999 | 0 |
| aca_62 | false | 21 | 21 | 21 | 607 | 0 |
| aca_63 | false | 21 | 21 | 21 | 1000 | 0 |
| aca_64 | false | 21 | 21 | 21 | 1000 | 0 |
| aca_65 | false | 21 | 21 | 21 | 1000 | 0 |
| aca_66 | false | 21 | 20 | 20 | 290 | 0 |
| aca_67 | false | 21 | 20 | 20 | 866 | 0 |
| aca_68 | false | 21 | 21 | 21 | 922 | 0 |
| aca_69 | false | 21 | 21 | 21 | 1000 | 0 |
| aca_70 | false | 21 | 21 | 21 | 1000 | 0 |
| aca_71 | false | 20 | 19 | 19 | 600 | 0 |
| aca_72 | false | 20 | 18 | 18 | 830 | 0 |
| aca_73 | false | 21 | 21 | 21 | 1000 | 0 |
| aca_74 | false | 21 | 21 | 21 | 1000 | 0 |
| aca_75 | false | 21 | 21 | 21 | 1000 | 0 |
| aca_76 | false | 21 | 21 | 21 | 1000 | 0 |
| aca_77 | false | 21 | 21 | 21 | 1000 | 0 |
| aca_78 | false | 21 | 19 | 19 | 886 | 0 |
| aca_79 | false | 21 | 21 | 21 | 548 | 0 |
| aca_80 | false | 21 | 19 | 19 | 1000 | 0 |
| aca_81 | false | 22 | 18 | 18 | 1000 | 0 |
| aca_82 | false | 22 | 22 | 22 | 805 | 0 |
| aca_83 | false | 22 | 22 | 22 | 1000 | 0 |
| aca_84 | false | 22 | 22 | 22 | 1000 | 0 |
| aca_85 | false | 22 | 18 | 18 | 1000 | 0 |
| aca_86 | false | 22 | 22 | 22 | 1000 | 0 |
| aca_87 | false | 23 | 20 | 20 | 1000 | 0 |
| aca_88 | false | 23 | 19 | 19 | 974 | 0 |
| aca_89 | false | 23 | 23 | 23 | 982 | 0 |
| aca_90 | false | 23 | 20 | 20 | 310 | 0 |
| aca_91 | false | 23 | 23 | 23 | 1000 | 0 |
| aca_92 | false | 23 | 23 | 23 | 1000 | 0 |
| aca_93 | false | 23 | 23 | 23 | 1000 | 0 |
| aca_94 | false | 23 | 23 | 23 | 623 | 0 |
| aca_95 | false | 21 | 19 | 19 | 568 | 0 |
| aca_96 | false | 23 | 23 | 23 | 1000 | 0 |
| aca_97 | false | 24 | 19 | 19 | 1000 | 0 |
| aca_98 | false | 24 | 19 | 19 | 1000 | 0 |
| aca_99 | false | 25 | 19 | 19 | 839 | 0 |
| aca_100 | false | 25 | 20 | 20 | 952 | 0 |
| aca_101 | false | 25 | 25 | 25 | 639 | 0 |
| aca_102 | false | 25 | 25 | 25 | 1000 | 0 |
| aca_103 | false | 25 | 25 | 25 | 1000 | 0 |
| aca_104 | false | 25 | 25 | 25 | 1000 | 0 |
| aca_105 | false | 25 | 21 | 21 | 602 | 0 |
| aca_106 | false | 25 | 21 | 21 | 1000 | 0 |
| aca_107 | false | 25 | 22 | 22 | 1000 | 0 |
| aca_108 | false | 25 | 24 | 24 | 1000 | 0 |
| aca_109 | false | 25 | 23 | 23 | 1000 | 0 |
| aca_110 | false | 25 | 22 | 22 | 1000 | 0 |
| aca_111 | false | 25 | 24 | 24 | 1000 | 0 |
| aca_112 | false | 25 | 24 | 24 | 1000 | 0 |
| aca_113 | false | 25 | 23 | 23 | 1000 | 0 |
| aca_114 | false | 25 | 23 | 23 | 1000 | 0 |
| aca_115 | false | 13 | 13 | 13 | 947 | 0 |
| aca_116 | false | 14 | 14 | 14 | 412 | 0 |
| aca_117 | false | 14 | 14 | 14 | 184 | 0 |
| aca_118 | false | 15 | 15 | 15 | 644 | 0 |
| aca_119 | false | 16 | 16 | 16 | 914 | 0 |
| aca_120 | false | 16 | 15 | 15 | 450 | 0 |
| aca_121 | false | 16 | 15 | 15 | 843 | 0 |
| aca_122 | false | 18 | 16 | 16 | 998 | 0 |
| aca_123 | false | 20 | 17 | 17 | 1000 | 0 |
