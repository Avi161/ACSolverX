"""W4: mu of the MMS02-corridor representative Q of AK(3)'s stable class.

Q = (xYxYXyyXYxyXy, XyyXYXyxYYxy) is the rank-2 pair obtained from the open
bridge triple Tpub = (A, B, Xyz) by Tietze-eliminating z (z = Yx), i.e. the
published MMS02 descendant pair; the corridor certifies AK(3) ~st Q. Every
mu/orbit/thickenability scan so far explored AK(3)'s CoV cone from its
canonical rep; Q arrived through the Wirtinger corridor and its Aut-orbit is
uncharted. This checker computes:

  1. aut_canon(Q): Aut(F2)-minimal total length mu(Q) and canonical rep,
     with the certificate check by pure substitution;
  2. the same for AK(3)'s own rep (control: known mu = 13);
  3. whether canon(Q) equals canon(AK3) (same Aut-orbit or a NEW stable rep);
  4. a 1,000-node greedy preflight from Q (repo budget law).

mu(Q) <= 12 would trip the MU_CRITERION aca_115 tripwire (presumed bug until
independently reproduced — it would settle an open problem stably).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from experiments.equivalence_classes.lib.autcanon import aut_canon, check
from experiments.stable_ac.solvern import Pres, search_n, str_to_word

Q = ("xYxYXyyXYxyXy", "XyyXYXyxYYxy")
AK3 = ("YXYxyx", "YYYYxxx")


def report(name, pair):
    t, rep, phi = aut_canon(pair)
    assert check(pair, rep, phi), f"aut_canon certificate FAILED for {name}"
    print(json.dumps({"pair": name, "input": list(pair), "mu": t,
                      "canon": list(rep)}))
    return t, rep


def main():
    mu_q, rep_q = report("Q(corridor)", Q)
    mu_ak3, rep_ak3 = report("AK3(control)", AK3)
    same = rep_q == rep_ak3
    print(json.dumps({"same_aut_orbit": same, "mu_q": mu_q,
                      "mu_ak3": mu_ak3}))
    if mu_ak3 != 13:
        print("CONTROL FAILURE: AK3 mu != 13; do not trust this run.")
        return 2
    if mu_q <= 12:
        print("TRIPWIRE: mu(Q) <= 12 — presumed bug until independently "
              "reproduced (MU_CRITERION rule 6). Quarantine.")
    rels = tuple(tuple(int(g) for g in str_to_word(s)) for s in Q)
    stats = search_n(Pres(2, rels), 1000)
    print(json.dumps({"greedy_from_Q": {
        "solved": stats["solved"],
        "nodes": stats["nodes_explored"],
        "min_total": stats["min_relator_length"],
        "path_length": stats["path_length"]}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
