"""Lane B: best-first search over the FULL stable-AC move set.

Moves per state (variable n_gen, up to --max_gen):
  * substitution — greedy_nrel.get_neighbors (AC1-AC3 composite; numba primitives are
    n_gen-agnostic; only its byte KEYING is capped, which we do not use)
  * stabilize    — add z=n_gen+1 with relator z.w^-1, w from a word bank over {x,y}
                   (letters +-1/+-2 are present in every reachable state)
  * eliminate    — Lemma-11 removal of any generator occurring exactly once in some
                   relator (this is the destabilization supermove plain greedy lacks)

Keying: per-relator canonical form via gn.canonical_relator (Booth, works for any
letter ids), bytes via presentation.word_bytes (GMAX=16), sorted, joined; prefixed by
n_gen. Incremental for substitution moves (only one relator changes).

Priority: total relator length + gen_penalty*(n_gen - base_ngen), depth tie-break.
Success: any trivial presentation <x1..xk | x1,...,xk> (single-letter relators covering
each generator; sign-insensitive — one AC2 from the positive form).

On success the path is retraced (parent pointers only; moves re-derived) and emitted
as a certificate whose steps are substitution / stabilize / eliminate — verifiable by
verify_certificate.py and the independent verifier.
"""
import heapq
import time
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ONEGEN = os.path.join(ROOT, "experiments", "stable_ac", "one_generator")
for p in (HERE, ONEGEN):
    if p not in sys.path:
        sys.path.insert(0, p)

import greedy_nrel as gn  # noqa: E402
from presentation import word_bytes  # noqa: E402
from stable_moves import LengthCapExceeded, eliminate, find_eliminable, stabilize  # noqa: E402

INT = gn.INT_DTYPE


def rel_bytes(r):
    """Canonical bytes of one relator (any generator ids), GMAX byte scheme."""
    return word_bytes([int(a) for a in gn.canonical_relator(np.asarray(r, dtype=INT))])


def state_key(relators, n_gen):
    parts = sorted((rel_bytes(r) for r in relators), key=lambda b: (len(b), b))
    return bytes([n_gen]) + b"\x00".join(parts)


def is_trivial(relators, n_gen):
    if len(relators) != n_gen:
        return False
    if any(len(r) != 1 for r in relators):
        return False
    return sorted(abs(int(r[0])) for r in relators) == list(range(1, n_gen + 1))


class StableSolver:
    def __init__(self, relators, n_gen, stabilize_bank=(), max_gen=3, max_nodes=100_000,
                 max_len=gn.L, gen_penalty=2):
        self.base_ngen = n_gen
        self.max_gen = max_gen
        self.max_nodes = max_nodes
        self.max_len = max_len
        self.gen_penalty = gen_penalty
        self.bank = [tuple(w) for w in stabilize_bank]
        self.start = (tuple(tuple(int(a) for a in r) for r in relators), n_gen)
        self.visited = {}      # key -> (parent_key, state, n_gen)  (state kept for retrace)
        self.min_total_len = None
        self.solved_key = None

    # ---- neighbor generation (state as tuple of int-tuples) -------------------

    def neighbors(self, relators, n_gen):
        """Yields (child_relators, child_ngen, step) for every legal move."""
        np_state = tuple(np.array(r, dtype=INT) for r in relators)
        for nbr, move in gn.get_neighbors(np_state, n_gen):
            ci = move[0]
            if len(nbr[ci]) >= self.max_len:
                continue
            child = tuple(tuple(int(a) for a in r) for r in nbr)
            yield child, n_gen, {"type": "substitution", "ci": int(ci)}
        if n_gen < self.max_gen:
            for w in self.bank:
                s, ng, step = stabilize(relators, n_gen, list(w))
                yield tuple(tuple(r) for r in s), ng, step
        for g, ri in find_eliminable(relators, n_gen):
            if n_gen <= 1:
                break
            try:
                s, ng, step = eliminate(relators, n_gen, g, ri, l_cap=self.max_len - 1)
            except (LengthCapExceeded, ValueError):
                continue
            if any(len(r) == 0 for r in s):
                continue
            yield tuple(tuple(r) for r in s), ng, step

    def solve(self):
        rel0, ng0 = self.start
        k0 = state_key(rel0, ng0)
        tl0 = sum(len(r) for r in rel0)
        self.min_total_len = tl0
        self.visited[k0] = (None, rel0, ng0)
        pq = [(tl0 + self.gen_penalty * (ng0 - self.base_ngen), 0, k0)]
        nodes = 0
        while pq and nodes < self.max_nodes:
            _, depth, key = heapq.heappop(pq)
            nodes += 1
            _, relators, n_gen = self.visited[key]
            if is_trivial(relators, n_gen):
                self.solved_key = key
                return nodes
            for child, ng, _step in self.neighbors(relators, n_gen):
                ck = state_key(child, ng)
                if ck in self.visited:
                    continue
                self.visited[ck] = (key, child, ng)
                tl = sum(len(r) for r in child)
                if tl + (ng - self.base_ngen) < self.min_total_len:
                    self.min_total_len = tl + (ng - self.base_ngen)
                if is_trivial(child, ng):
                    self.solved_key = ck
                    return nodes
                heapq.heappush(pq, (tl + self.gen_penalty * (ng - self.base_ngen),
                                    depth + 1, ck))
        return nodes

    def retrace(self):
        """(states_with_ngen, steps) from the start to the solved state; each step
        re-derived by regenerating the parent's neighbors."""
        assert self.solved_key is not None
        chain = []
        k = self.solved_key
        while k is not None:
            parent, relators, n_gen = self.visited[k]
            chain.append((k, relators, n_gen))
            k = parent
        chain.reverse()
        states = [(list(map(list, relators)), ng) for _, relators, ng in chain]
        steps = []
        for t in range(1, len(chain)):
            key_t, _, _ = chain[t]
            _, prel, png = chain[t - 1]
            found = None
            for child, ng, step in self.neighbors(prel, png):
                if state_key(child, ng) == key_t:
                    found = (child, ng, step)
                    break
            assert found is not None, "retrace: move not re-derivable"
            # certificate states must be the exact post-move states (not canonical)
            states[t] = ([list(r) for r in found[0]], found[1])
            steps.append(found[2])
        return states, steps


def solve_one(relators, n_gen, bank, max_gen=3, max_nodes=100_000, max_len=gn.L,
              gen_penalty=2, name="", emit_cert_path=None):
    t0 = time.time()
    s = StableSolver(relators, n_gen, stabilize_bank=bank, max_gen=max_gen,
                     max_nodes=max_nodes, max_len=max_len, gen_penalty=gen_penalty)
    nodes = s.solve()
    dt = time.time() - t0
    rec = {"name": name, "solved": s.solved_key is not None, "nodes": int(nodes),
           "min_total_len": int(s.min_total_len), "wall_s": round(dt, 1),
           "max_gen": max_gen, "max_len": max_len, "bank_size": len(bank),
           "gen_penalty": gen_penalty, "budget": max_nodes}
    if s.solved_key is not None:
        states, steps = s.retrace()
        rec["path_len"] = len(steps)
        if emit_cert_path:
            from certificate import make_certificate, save_certificate
            from verify_certificate import verify
            cert = make_certificate(
                name=f"laneB_{name}", claim=f"Stable-AC trivialization found by "
                f"StableSolver from {name}.", states_with_ngen=states, steps=steps,
                end_is_trivial=True,
                meta={"solver": "StableSolver", "budget": max_nodes})
            ok, errs = verify(cert)
            rec["cert_verified"] = ok
            rec["cert_errors"] = errs[:5]
            save_certificate(cert, emit_cert_path)
            rec["cert_path"] = emit_cert_path
    return rec
