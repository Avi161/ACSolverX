| Floor class | Count | Share | Relators |
|---|---|---|---|
| Class 1 (= laneF's F) | 712 | 70.8% | YYxyXX, YYYXXyx |
| Class 2 (= AK(3)) | 294 | 29.2% | YXYxyx, YYYxxxx |

*Note: Floor class = the greedy search's canonical terminal state (floor_mkey, min over signed relabelings) after re-solving every merged Lane-D quotient at a 25,000-node budget; all 1,006 probes bottom out at total relator length 13 in exactly 2 distinct classes.*

*Note: Relator words translate the int-array floor_state (1=x, -1=X, 2=y, -2=Y).*

*Note: Identity check (mitm.symmetry_keys, live): the majority class's floor state is the laneF_F_to_AK3 cert's F start state (mod signed relabeling); the minority class's floor state is AK(3) itself (mod signed relabeling).*
