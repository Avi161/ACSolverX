"""Certificate format for stable-AC equivalence chains (data layer only — no checking).

A certificate is a JSON object:

{
  "certificate_version": "1",
  "name": "...",
  "claim": "...",                       # human-readable statement being certified
  "start": {"n_gen": k, "relators": [[...], ...]},
  "end":   {"n_gen": k', "relators": [[...], ...]},
  "end_is_trivial": bool,               # end must be <x1..xk' | x1, ..., xk'>
  "steps": [ step, ... ],               # length T
  "states": [ state, ... ],            # length T+1; states[0]==start, states[-1]==end
  "meta": {...}                         # provenance: source paper/lines, generators, etc.
}

Step types (see stable_moves.py / hmoves.py for emitters):
  concat        {i, j, sign}            AC'1: r_i -> free_reduce(r_i . r_j^sign)
  conjugation   {i, g}                  AC'2: r_i -> free_reduce(g . r_i . g^-1)
  stabilize     {z, w}                  add generator z=n_gen+1, relator cyclic_reduce(z . w^-1)
  eliminate     {gen, ri, ...}          Lemma-11: remove gen via relator ri (exactly-once occurrence);
                                        generators > gen renumbered down by 1
  relabel       {perm, invert}          signed generator permutation (AC-equivariant renaming)
  substitution  {ci, a, b, i, j, c_inv} greedy_nrel composite move; verified by membership in
                                        the recomputed neighbor set (states are canonical tuples)

Soundness of a verified certificate: concat/conjugation/substitution are AC1-AC3 composites;
stabilize/eliminate are stable-AC equivalences by Lemma 11 of arXiv:2408.15332 (valid when the
presentation presents the trivial group — every move preserves the presented group, so triviality
propagates from the start); relabel is a signed free-group automorphism of the generator set,
under which AC1-AC5 sequences are equivariant.
"""
import json
import os

VERSION = "1"


def state_obj(relators, n_gen):
    return {"n_gen": int(n_gen), "relators": [[int(a) for a in r] for r in relators]}


def make_certificate(name, claim, states_with_ngen, steps, end_is_trivial=False, meta=None):
    """states_with_ngen: list of (state, n_gen) pairs, length len(steps)+1."""
    if len(states_with_ngen) != len(steps) + 1:
        raise ValueError("need len(states) == len(steps) + 1")
    states = [state_obj(s, g) for s, g in states_with_ngen]
    return {
        "certificate_version": VERSION,
        "name": name,
        "claim": claim,
        "start": states[0],
        "end": states[-1],
        "end_is_trivial": bool(end_is_trivial),
        "steps": steps,
        "states": states,
        "meta": meta or {},
    }


def save_certificate(cert, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        json.dump(cert, f)
        f.write("\n")


def load_certificate(path):
    with open(path) as f:
        return json.load(f)


def concat_certificates(name, claim, certs, meta=None):
    """Chain compatible certificates (end of one == start of next, exactly)."""
    states, steps = [], []
    for k, c in enumerate(certs):
        if k == 0:
            states.extend(c["states"])
        else:
            if c["states"][0] != states[-1]:
                raise ValueError(f"certificate {k} does not start where {k-1} ends")
            states.extend(c["states"][1:])
        steps.extend(c["steps"])
    out = {
        "certificate_version": VERSION,
        "name": name,
        "claim": claim,
        "start": states[0],
        "end": states[-1],
        "end_is_trivial": certs[-1]["end_is_trivial"],
        "steps": steps,
        "states": states,
        "meta": meta or {"chained_from": [c["name"] for c in certs]},
    }
    return out
