"""CPU port (no JAX) of Ryan Zang's MS640 CoV-gate best-first search.

Source: https://github.com/ryanzang04/Stable-ACSolver (MIT, Math & AI Lab at Caltech), files
scripts/ms640_cov_gates.py, scripts/greedy_search_n.py and envs/ac_moves.py, at commit 148a3de.

Same algorithm, rank two only (max_n_gen = n_gen = 2):
- per-relator cap 24 (a move whose result would be longer is a no-op), total cap 48 (children longer are dropped);
- substitution actions and change-of-variables (CoV) actions enumerated in Ryan's order, applied with the
  semantics of envs/ac_moves.py (s_move, _concatenate, cyclic_reduce, _change_of_variables), including the
  check of the seam-reduced length against 24 before cyclic reduction;
- canonical form, heap order (total length, depth, insertion), dedup and the six gates of ms640_cov_gates.py.

`tests`: benchmark/ryan/check_port.py compares every child with the JAX apply_batch and whole searches with
Ryan's script. Output records keep the schema of ms640_cov_gates.py.

Usage:
  python benchmark/ryan/cov_gates_cpu.py --input data/ms640_solved.txt --output out.jsonl --gate periodic10 \
      [--start 0 --end 640 --max-nodes 1000000]
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import heapq
import json
import os
import time
from pathlib import Path

GATES = ("no_short_sub", "short_relator", "unbalanced", "long_presentation", "plateau100", "periodic10")
# Ryan's caps are 24 per relator and 48 in total. set_caps(None, None) removes them (no length limit at all).
MAX_LENGTH = 24
MAX_TOTAL = 48
UNBOUNDED = 1 << 60


def set_caps(max_length=24, max_total=48):
    global MAX_LENGTH, MAX_TOTAL
    MAX_LENGTH = UNBOUNDED if max_length is None else int(max_length)
    MAX_TOTAL = UNBOUNDED if max_total is None else int(max_total)
N = 2  # active and max generators

# letter order Y < y < X < x (codes -2 < 2 < -1 < 1 in this order), as letter_order with active_n_gen = 2
ORDER = {-2: 0, 2: 1, -1: 2, 1: 3}
UNORDER = {v: k for k, v in ORDER.items()}


# ---------------------------------------------------------------- words (greedy_search_n.py semantics)
def inverse_word(w):
    return tuple(-c for c in reversed(w))


def free_reduce(w):
    s = []
    for c in w:
        if c == 0:
            continue
        if s and s[-1] == -c:
            s.pop()
        else:
            s.append(c)
    return s


def cyclic_reduce(w):
    r = free_reduce(w)
    while len(r) > 1 and r[0] == -r[-1]:
        r = free_reduce(r[1:-1])
    return tuple(r)


def _min_rotation_ordered(o):
    if len(o) <= 1:
        return o
    return min(o[i:] + o[:i] for i in range(len(o)))


def canonical_word(w):
    r = cyclic_reduce(w)
    if not r:
        return ()
    a = _min_rotation_ordered(tuple(ORDER[c] for c in r))
    b = _min_rotation_ordered(tuple(ORDER[c] for c in reversed([-c for c in r])))
    return tuple(UNORDER[c] for c in min(a, b))


def canonical_key(r0, r1):
    a, b = canonical_word(r0), canonical_word(r1)
    ka = (len(a), tuple(ORDER[c] for c in a))
    kb = (len(b), tuple(ORDER[c] for c in b))
    return (N, (a, b) if ka <= kb else (b, a))


def total_length(key):
    return len(key[1][0]) + len(key[1][1])


def is_trivial(key):
    a, b = key[1]
    return len(a) == 1 and len(b) == 1 and {abs(a[0]), abs(b[0])} == {1, 2}


# ---------------------------------------------------------------- actions (Ryan's enumeration order)
def substitution_actions(key):
    t, s = key[1]
    if not t or not s:
        return []
    out = []
    for tp, tc in enumerate(t):
        k = tp + 1
        for sp, sc in enumerate(s):
            if tc == -sc:
                out.append((0, 0, k, sp))
                out.append((1, 0, k, sp))
            if tc == sc:
                out.append((0, 1, k, -sp - 1))
                out.append((1, 1, k, -sp - 1))
    return out


def cov_actions(key, min_len=1, margin=1):
    out = []
    rels = key[1]
    for remove_gen in range(N):
        old = remove_gen + 1
        for iso, word in enumerate(rels):
            L = len(word)
            if L <= 1:
                continue
            branch = 2 + remove_gen * N + iso
            for z_start in range(L):
                rot = word[z_start:] + word[:z_start]
                for z_len in range(min_len, L - margin + 1):
                    if sum(1 for c in rot[z_len:] if abs(c) == old) != 1:
                        continue
                    out.append((branch, 0, z_start, z_len - 1))
                    out.append((branch, 1, z_start, z_len - 1))
    return out


# ---------------------------------------------------------------- moves (envs/ac_moves.py semantics)
def _rotate(w, k):
    if not w:
        return w
    k %= len(w)
    return w[k:] + w[:k]


def apply_substitution(key, action):
    """s_move with max_n_gen = 2: slot i <- reduce(rot_k1(r0) * rot_k2(r1 or r1^-1)); None if a no-op."""
    i, r, k1, k2 = action
    r0, r1 = key[1]
    rel1 = _rotate(r0, k1)
    rel2 = _rotate(inverse_word(r1) if r == 1 else r1, k2)
    l1, l2 = len(rel1), len(rel2)
    # _concatenate: num_cancel = argmin(rel2 == -reverse(rel1)) over the padded slot (first False; 0 if none)
    rev = tuple(reversed(rel1))
    nc = 0
    for j in range(max(l1, l2) + 1):
        a = rel2[j] if j < l2 else 0
        b = rev[j] if j < l1 else 0
        if a != -b:
            nc = j
            break
    else:
        nc = 0
    if l1 + l2 - 2 * nc > MAX_LENGTH:
        return None  # do_nothing: new relator == rel1, so the move is skipped
    word = rel1[: l1 - nc] + rel2[nc:]
    # cyclic_reduce on the padded slot: first index where word[i] != -reverse(word)[i], else MAX_LENGTH
    L = len(word)
    rw = tuple(reversed(word))
    c = L  # no mismatch at all: the slot reduces to nothing (as JAX with c = max_length)
    for j in range(L):
        if word[j] != -rw[j]:
            c = j
            break
    new = word[c: L - c] if L - 2 * c > 0 else ()
    if new == rel1:
        return None
    return canonical_key(new, r1) if i == 0 else canonical_key(r0, new)


def _substitute(word, old, expr):
    inv = inverse_word(expr)
    out = []
    for c in word:
        if c == old:
            out.extend(expr)
        elif c == -old:
            out.extend(inv)
        else:
            out.append(c)
    return out


def apply_cov(key, action):
    """_change_of_variables; None when the move is rejected (a no-op)."""
    branch, z_inverse, z_start, z_len_code = action
    remove_gen, iso = divmod(branch - 2, N)
    old = remove_gen + 1
    z_len = z_len_code + 1
    rels = key[1]
    w = rels[iso]
    L = len(w)
    if not (L > 1 and z_start < L and z_len < L):
        return None
    rot = w[z_start:] + w[:z_start]
    window, comp = rot[:z_len], rot[z_len:]
    z_word = inverse_word(window) if z_inverse == 1 else window
    hits = [p for p, c in enumerate(comp) if abs(c) == old]
    if len(hits) != 1:
        return None
    p = hits[0]
    token, before, after = comp[p], comp[:p], comp[p + 1:]
    z_rhs = old if z_inverse == 1 else -old
    if token == old:
        expr = list(inverse_word(before)) + [z_rhs] + list(inverse_word(after))
    else:
        expr = list(after) + [-z_rhs] + list(before)
    expr = tuple(free_reduce(expr))
    if len(expr) > MAX_LENGTH:
        return None
    definition = cyclic_reduce([old] + _substitute(inverse_word(z_word), old, expr))
    if len(definition) > MAX_LENGTH:
        return None
    other = 1 - iso
    sub = cyclic_reduce(_substitute(rels[other], old, expr))
    if len(sub) > MAX_LENGTH:
        return None
    new = [None, None]
    new[iso], new[other] = definition, sub
    return canonical_key(new[0], new[1])


def apply(key, action):
    return apply_substitution(key, action) if action[0] < 2 else apply_cov(key, action)


# ---------------------------------------------------------------- compact state storage
# A state is stored as bytes (letter codes shifted to 1..4, relators split by 0); the heap holds one int per
# entry, (length, depth, seq) packed so that int order equals tuple order. seq is also the state's id.
_ENC = {-2: 1, -1: 2, 1: 3, 2: 4}
_DEC = {1: -2, 2: -1, 3: 1, 4: 2}
_SEQ_BITS, _DEPTH_BITS = 36, 22


def encode(key):
    a, b = key[1]
    return bytes([_ENC[c] for c in a]) + b"\x00" + bytes([_ENC[c] for c in b])


def decode(blob):
    i = blob.index(0)
    return (N, (tuple(_DEC[c] for c in blob[:i]), tuple(_DEC[c] for c in blob[i + 1:])))


def _pack(length, depth, seq):
    return (length << (_DEPTH_BITS + _SEQ_BITS)) | (depth << _SEQ_BITS) | seq


def _unpack(v):
    return v >> (_DEPTH_BITS + _SEQ_BITS), (v >> _SEQ_BITS) & ((1 << _DEPTH_BITS) - 1), v & ((1 << _SEQ_BITS) - 1)


# ---------------------------------------------------------------- search (ms640_cov_gates.search)
def search(start_key, gate, max_nodes, progress_seconds=60.0, label=""):
    from array import array
    ids = {encode(start_key): 0}       # state -> id (= insertion seq)
    blobs = [encode(start_key)]        # id -> state
    parent = array("q", [-1])          # id -> parent id
    act = [None]                       # id -> action that produced it (tuple)
    queue = [_pack(total_length(start_key), 0, 0)]
    seq = visited = checks = openings = cov_enum = cov_changed = cov_shorter = cov_shorter_unique = 0
    openings_shorter = 0
    best_length = total_length(start_key)
    last_improved = 0
    start = time.monotonic()
    last_report = start

    def expand(key, depth, actions, family, pid):
        nonlocal seq, cov_changed, cov_shorter, cov_shorter_unique
        current = total_length(key)
        shorter = set()
        for action in actions:
            nxt = apply(key, action)
            if nxt is None or nxt == key:
                continue
            length = total_length(nxt)
            if length > MAX_TOTAL:
                continue
            blob = encode(nxt)
            if family == "cov":
                cov_changed += 1
                if length < current:
                    cov_shorter += 1
                    shorter.add(blob)
            elif length < current:
                shorter.add(blob)
            if blob in ids:
                continue
            seq += 1
            ids[blob] = seq
            blobs.append(blob)
            parent.append(pid)
            act.append(action)
            heapq.heappush(queue, _pack(length, depth + 1, seq))
        if family == "cov":
            cov_shorter_unique += len(shorter)
        return bool(shorter)

    while queue and visited < max_nodes:
        length, depth, sid = _unpack(heapq.heappop(queue))
        key = decode(blobs[sid])
        visited += 1
        if is_trivial(key):
            keys, actions = [], []
            cur = sid
            while cur != -1:
                keys.append(decode(blobs[cur]))
                if act[cur] is not None:
                    actions.append(act[cur])
                cur = parent[cur]
            keys.reverse()
            actions.reverse()
            return _result(True, "solved", visited, len(ids), checks, openings, cov_enum, cov_changed,
                           cov_shorter, cov_shorter_unique, openings_shorter, start, keys, actions, best_length)
        if length < best_length:
            best_length, last_improved = length, visited
        sub_shortens = expand(key, depth, substitution_actions(key), "sub", sid)
        checks += 1
        lens = [len(w) for w in key[1]]
        should_open = {
            "no_short_sub": not sub_shortens,
            "short_relator": min(lens) <= 3,
            "unbalanced": max(lens) >= 2 * min(lens),
            "long_presentation": length >= 16,
            "plateau100": visited - last_improved >= 100,
            "periodic10": visited % 10 == 0,
        }[gate]
        if should_open:
            openings += 1
            moves = cov_actions(key)
            cov_enum += len(moves)
            openings_shorter += int(expand(key, depth, moves, "cov", sid))
        now = time.monotonic()
        if now - last_report >= progress_seconds:
            print(f"progress {label} gate={gate} visited={visited} seen={len(ids)} openings={openings} "
                  f"elapsed={now - start:.1f}s", flush=True)
            last_report = now
    return _result(False, "budget" if queue else "frontier_exhausted", visited, len(ids), checks, openings,
                   cov_enum, cov_changed, cov_shorter, cov_shorter_unique, openings_shorter, start, [], [],
                   best_length)


def _payload(key):
    letters = {1: "x", -1: "X", 2: "y", -2: "Y"}
    return {"n_gen": 2, "relators": [list(w) for w in key[1]],
            "relators_text": ["".join(letters[c] for c in w) for w in key[1]]}


def _result(solved, reason, visited, n_seen, checks, openings, actions, changed, shorter, shorter_unique,
            openings_shorter, started, keys, path_actions, best_length):
    n_cov = sum(1 for a in path_actions if a[0] >= 2)
    return {"solved": solved, "termination": reason, "nodes_visited": visited, "states_seen": n_seen,
            "elapsed_sec": round(time.monotonic() - started, 3),
            "path_length": len(path_actions) if solved else None,
            "path_sub_moves": (len(path_actions) - n_cov) if solved else None,
            "path_cov_moves": n_cov if solved else None,
            "max_relator_len": max(max(len(w) for w in k[1]) for k in keys) if solved else None,
            "max_total_len": max(total_length(k) for k in keys) if solved else None,
            "path": [_payload(k) for k in keys], "actions": [list(a) for a in path_actions],
            "gate_checks": checks, "gate_openings": openings, "cov_actions_enumerated": actions,
            "cov_changed_in_cap_actions": changed, "cov_shortening_actions": shorter,
            "cov_shortening_unique_per_parent_sum": shorter_unique,
            "gate_openings_with_shortening": openings_shorter, "best_popped_length": best_length}


def start_key_from_row(raw):
    """A 48-entry row (two relators padded to 24) -> canonical key, as normalize_dataset_flat + canonicalize_flat."""
    if len(raw) != 48 or any(x not in (-2, -1, 0, 1, 2) for x in raw):
        raise ValueError("invalid 48-entry rank-two row")
    r0 = tuple(c for c in raw[:24] if c)   # the input format pads each relator to 24, whatever the caps
    r1 = tuple(c for c in raw[24:] if c)
    return canonical_key(r0, r1)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, help="one 48-entry row per line (data/ms640_solved.txt format)")
    p.add_argument("--output", required=True)
    p.add_argument("--gate", choices=GATES, required=True)
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--end", type=int, default=None)
    p.add_argument("--max-nodes", type=int, default=1_000_000)
    p.add_argument("--progress-seconds", type=float, default=60)
    a = p.parse_args()
    lines = [l for l in Path(a.input).read_text().splitlines() if l.strip()]
    end = len(lines) if a.end is None else a.end
    config = {"dataset_sha256": hashlib.sha256(Path(a.input).read_bytes()).hexdigest(), "gate": a.gate,
              "max_nodes": a.max_nodes, "max_length": MAX_LENGTH, "max_total_length": MAX_TOTAL,
              "cov_window_min_length": 1, "cov_window_relator_margin": 1, "engine": "cpu_port",
              "port_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        for line in out.read_text().splitlines():
            rec = json.loads(line)
            if rec["config"] != config:
                raise SystemExit(f"configuration mismatch in {out}; choose a new output file")
            done.add(rec["idx"])
    with out.open("a", buffering=1) as f:
        for idx in range(a.start, end):
            if idx in done:
                continue
            key = start_key_from_row(ast.literal_eval(lines[idx]))
            data = search(key, a.gate, a.max_nodes, a.progress_seconds, label=f"idx={idx}")
            data.update(idx=idx, config=config)
            f.write(json.dumps(data, separators=(",", ":")) + "\n")
            f.flush()
            os.fsync(f.fileno())
            print(f"done gate={a.gate} idx={idx} solved={data['solved']} nodes={data['nodes_visited']} "
                  f"seen={data['states_seen']} path={data['path_length']}", flush=True)


if __name__ == "__main__":
    main()
