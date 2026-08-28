"""W2 verifier: independent replay of the period-two census hits.

Reads the 17 chains printed by period_two_solution_census.py (embedded below
as a frozen fixture) and re-checks each condition from scratch using ONLY
conjugacy-class normal forms — a different formulation from the generator,
which constructed R, S, U by explicit conjugate enumeration:

    (1)  cyc(R^-1 A)  == cyc(B)      <=>  R in A * Cl(B^-1)
    (2)  cyc(S^-1 B)  == cyc(R)      <=>  S in B * Cl(R^-1)
    (3)  cyc(U^-1 R)  == cyc(S)      <=>  U in R * Cl(S^-1)   [R^-1 U in Cl(S^-1)]
    (4)  exists g, len(g) <= 6:  cyc(U g t g^-1) == cyc(S)
                                  <=>  Z = U^-1 h3 S h3^-1 in Cl(t)
    (5)  S hyperbolic (cyc(S) != "c")  [elliptic obstruction cross-check]

Any failure is a generator bug. The fixture is the exact sorted chain list
from the census run at CAP=12, GPAD=5.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from period_two_solution_census import A, B, ball, cyc_form, inv, mul

CHAINS_FILE = Path(__file__).resolve().parent / "period_two_census_chains.json"


def main():
    chains = json.loads(CHAINS_FILE.read_text())
    cf_b = cyc_form(B)
    ok = 0
    for R, S, U in chains:
        assert cyc_form(mul(inv(R), A)) == cf_b, ("cond1", R)
        assert cyc_form(mul(inv(S), B)) == cyc_form(R), ("cond2", R, S)
        assert cyc_form(mul(inv(U), R)) == cyc_form(S), ("cond3", R, S, U)
        cf_s = cyc_form(S)
        assert cf_s != "c", ("elliptic S", S)
        found = False
        for g in ball(6):
            if cyc_form(mul(U, g, "t", inv(g))) == cf_s:
                found = True
                break
        assert found, ("cond4", R, S, U)
        ok += 1
    print(f"ALL {ok} CHAINS VERIFY (independent cyclic-form replay)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
