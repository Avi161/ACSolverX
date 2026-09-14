# Executed bounded algebraic probes

Gains below compare with the frozen phase baseline and every imported seed for that run. They are not necessarily first discoveries across separate runs. Each row receives at most 1,000 newly charged algebraic checks; these are not equivalent to heap pops. Times exclude verification, cooldown and historical seed discovery.

The separate `primitive_search_results_corrected.json` records two bounded S20 continuations and is excluded from this algebraic-probe index.

| Result file | Rows | Gains beyond seeds | Units | CPU s | Wall s | Max generated rank |
|---|---:|---|---:|---:|---:|---:|
| [aliases_v3_pilot.json](aliases_v3_pilot.json) | 11 | none | 11000 | 0.069978 | 0.072541 | 4 |
| [aliases_v3_rank2.json](aliases_v3_rank2.json) | 35 | none | 35000 | 0.119913 | 0.121438 | 4 |
| [aut_collect_pilot21.json](aut_collect_pilot21.json) | 21 | none | 19032 | 0.303244 | 0.304523 | 5 |
| [aut_collect_remaining103.json](aut_collect_remaining103.json) | 103 | none | 50583 | 1.180523 | 1.198824 | 5 |
| [central_exchange_all33.json](central_exchange_all33.json) | 33 | none | 33000 | 1.049419 | 1.056932 | 4 |
| [collector_aliases_pilot17.json](collector_aliases_pilot17.json) | 17 | none | 17000 | 0.354471 | 0.355381 | 5 |
| [collector_aliases_remaining107.json](collector_aliases_remaining107.json) | 107 | aca_5 (+1) | 107000 | 2.251205 | 2.264645 | 5 |
| [collector_left_all124.json](collector_left_all124.json) | 124 | none | 124000 | 2.393363 | 2.408388 | 8 |
| [collector_pilot.json](collector_pilot.json) | 11 | none | 11000 | 0.165099 | 0.165529 | 7 |
| [collector_prefix_pilot.json](collector_prefix_pilot.json) | 15 | none | 15000 | 0.313262 | 0.314301 | 5 |
| [collector_prefix_remaining109.json](collector_prefix_remaining109.json) | 109 | aca_44 (+1), aca_56 (+1) | 109000 | 2.371065 | 2.383288 | 5 |
| [collector_remaining113.json](collector_remaining113.json) | 113 | aca_43 (+1), aca_67 (+1), aca_79 (+1), aca_87 (+1), aca_88 (+1), aca_106 (+1) | 113000 | 1.842775 | 1.852958 | 7 |
| [collector_right_all124.json](collector_right_all124.json) | 124 | none | 124000 | 2.841913 | 2.849344 | 14 |
| [collector_second_pass13.json](collector_second_pass13.json) | 13 | none | 13000 | 0.186033 | 0.186520 | 7 |
| [commutators_pilot.json](commutators_pilot.json) | 10 | none | 10000 | 0.232839 | 0.233808 | 3 |
| [completion_pilot.json](completion_pilot.json) | 9 | none | 9000 | 1.548367 | 1.549516 | 4 |
| [conjugacy_rank2.json](conjugacy_rank2.json) | 35 | none | 14816 | 0.070018 | 0.070335 | 3 |
| [conjugate_bridge_all33.json](conjugate_bridge_all33.json) | 33 | none | 33000 | 0.970603 | 0.972786 | 5 |
| [conjugate_exchange_all33.json](conjugate_exchange_all33.json) | 33 | none | 33000 | 1.159039 | 1.160847 | 4 |
| [corridor_pilot.json](corridor_pilot.json) | 7 | none | 2709 | 0.024390 | 0.024402 | 3 |
| [corridor_remaining_roots.json](corridor_remaining_roots.json) | 36 | none | 14801 | 0.203487 | 0.205062 | 4 |
| [dictionary_exchange_all124.json](dictionary_exchange_all124.json) | 124 | none | 87292 | 3.610034 | 3.623378 | 5 |
| [dictionary_exchange_pilot.json](dictionary_exchange_pilot.json) | 11 | none | 11000 | 0.419817 | 0.421239 | 3 |
| [donor_relative_pilot.json](donor_relative_pilot.json) | 10 | none | 10000 | 0.047444 | 0.050097 | 4 |
| [endpoint_closure_all124.json](endpoint_closure_all124.json) | 124 | none | 946 | 0.095834 | 0.097176 | 3 |
| [flow_exact_diagnostic.json](flow_exact_diagnostic.json) | 124 | none | 11191 | 0.063358 | 0.064657 | 4 |
| [flow_exact_pilot.json](flow_exact_pilot.json) | 7 | none | 3027 | 0.012211 | 0.012200 | 3 |
| [multi_metric_pilot.json](multi_metric_pilot.json) | 11 | none | 1737 | 0.034665 | 0.034873 | 3 |
| [neutral_after_collector.json](neutral_after_collector.json) | 11 | none | 7818 | 0.528342 | 0.530131 | 5 |
| [neutral_aut_exchange_pilot17.json](neutral_aut_exchange_pilot17.json) | 17 | none | 15032 | 0.314581 | 0.315305 | 5 |
| [neutral_aut_exchange_remaining107.json](neutral_aut_exchange_remaining107.json) | 107 | aca_99 (+1) | 54583 | 1.278675 | 1.296704 | 5 |
| [nonoverlap_products_all124.json](nonoverlap_products_all124.json) | 124 | none | 124000 | 3.005425 | 3.030939 | 5 |
| [peeling_all124.json](peeling_all124.json) | 124 | none | 5182 | 0.389972 | 0.396468 | 4 |
| [plateau_pilot.json](plateau_pilot.json) | 6 | none | 3569 | 0.226444 | 0.231347 | 4 |
| [plateau_remainder.json](plateau_remainder.json) | 118 | aca_75 (+1), aca_83 (+1), aca_84 (+1) | 24738 | 2.274531 | 2.279862 | 4 |
| [plateau_whitehead_pilot.json](plateau_whitehead_pilot.json) | 6 | none | 6000 | 0.138876 | 0.139415 | 4 |
| [plateau_whitehead_remainder.json](plateau_whitehead_remainder.json) | 118 | aca_75 (+1), aca_83 (+1), aca_84 (+1) | 50835 | 1.748389 | 1.767088 | 4 |
| [primitive_root_pilot.json](primitive_root_pilot.json) | 9 | none | 570 | 0.027699 | 0.028608 | 3 |
| [root_metric_pilot.json](root_metric_pilot.json) | 9 | aca_101 (+1) | 4375 | 0.033393 | 0.033548 | 3 |
| [root_metric_remaining.json](root_metric_remaining.json) | 32 | none | 17431 | 0.094158 | 0.104426 | 3 |
| [root_templates_pilot.json](root_templates_pilot.json) | 10 | none | 9817 | 0.084700 | 0.085158 | 5 |
| [schreier_descend_pilot.json](schreier_descend_pilot.json) | 11 | none | 11000 | 0.190932 | 0.191853 | 8 |
| [schreier_pilot.json](schreier_pilot.json) | 11 | none | 11000 | 0.156335 | 0.157028 | 22 |
| [stable_metric_pilot.json](stable_metric_pilot.json) | 11 | none | 1737 | 0.047076 | 0.047106 | 3 |
| [stable_metric_remaining32.json](stable_metric_remaining32.json) | 32 | none | 21739 | 0.298179 | 0.298637 | 3 |
| [stable_metric_v2_all33.json](stable_metric_v2_all33.json) | 33 | none | 13054 | 0.294112 | 0.301050 | 3 |
| [templates_pilot.json](templates_pilot.json) | 9 | none | 9000 | 0.095602 | 0.102280 | 5 |
| [templates_remainder.json](templates_remainder.json) | 115 | aca_95 (+1) | 115000 | 1.949677 | 1.979448 | 5 |
| [templates_v2_pilot.json](templates_v2_pilot.json) | 9 | none | 9000 | 0.083084 | 0.083418 | 4 |
| [templates_v2_remainder.json](templates_v2_remainder.json) | 115 | none | 115000 | 1.127294 | 1.139697 | 5 |
| [torus_exchange_all33.json](torus_exchange_all33.json) | 33 | none | 33000 | 1.092598 | 1.101468 | 4 |
| [universal_metric_nonbs.json](universal_metric_nonbs.json) | 10 | none | 2415 | 0.115886 | 0.116133 | 4 |
| [uphill_score_all124.json](uphill_score_all124.json) | 124 | none | 124000 | 3.195672 | 3.217778 | 5 |
| [uphill_whitehead_all124.json](uphill_whitehead_all124.json) | 124 | aca_72 (+1), aca_80 (+1), aca_111 (+1) | 124000 | 3.869630 | 3.901657 | 5 |
| [uphill_whitehead_pilot.json](uphill_whitehead_pilot.json) | 14 | none | 14000 | 0.425602 | 0.426771 | 3 |
