"""Beam-search decode of a trained policy -- the evaluation path.

Mirrors `beam/beam_search.py`: score `cum_log_prob + log_softmax + alpha*value`,
take the global top-`B` over `beam x action`, kill no-ops, drop duplicate states
within the step, and drop states any beam has already visited in this search.
Defaults match its argparse (`beam_width 1024`, `max_steps 150`, `alpha 0`,
`temperature 0`), so a run here is comparable to a run there.

Two deviations, both documented rather than hidden:

- **Dedup hashing is 64-bit, upstream is 32-bit.** Upstream's global buffer holds
  `B * T = 153,600` int32 hashes, where the birthday bound makes several
  collisions near-certain, and each collision kills a live beam that had done
  nothing wrong. A 64-bit hash makes that probability ~1e-9. It can only help or
  be neutral, never hurt, but it does mean this is not a bit-identical replay.
- The hash vector is torch-seeded; `jax.random.randint(PRNGKey(0xACABDED))` is
  not reproducible outside JAX. Identical states still hash identically, which
  is the only property dedup needs.

Results go to jsonl, one row per presentation, resumable: a run re-reads the
file and skips presentations already recorded.
"""

import json
import os
import time

import numpy as np
import torch

from experiments.ppo.acs_moves import decode_action, s_move

SENTINEL = torch.iinfo(torch.int64).max


def make_hash_vec(obs_len, device, seed=0xACABDED):
    gen = torch.Generator(device="cpu")
    gen.manual_seed(seed)
    v = torch.randint(-(2 ** 62), 2 ** 62, (obs_len,), generator=gen, dtype=torch.int64)
    return v.to(device)


def _hash(x, hash_vec):
    return (x * hash_vec).sum(-1)


@torch.no_grad()
def _forward(model, x, chunk):
    if x.shape[0] <= chunk:
        return model(x)
    lg, vl = [], []
    for lo in range(0, x.shape[0], chunk):
        a, b = model(x[lo:lo + chunk])
        lg.append(a)
        vl.append(b)
    return torch.cat(lg), torch.cat(vl)


@torch.no_grad()
def beam_search_one(model, x0, hash_vec, *, n_gen=2, max_length=24, beam_width=1024,
                    max_steps=150, alpha=0.0, temperature=0.0, temp_end=0.0,
                    generator=None, chunk=4096):
    """Search one presentation. Returns `(solved, path_length, [flat actions])`."""
    device = x0.device
    L, B, T = max_length, beam_width, max_steps
    n_actions = n_gen * 2 * L * L
    neg_inf = float("-inf")

    states = x0.unsqueeze(0).expand(B, -1).clone()
    alive = torch.ones(B, dtype=torch.bool, device=device)
    cum = torch.full((B,), neg_inf, dtype=torch.float32, device=device)
    cum[0] = 0.0                                     # only beam 0 is real at t=0
    seqs = torch.full((B, T), -1, dtype=torch.int64, device=device)

    cap = B * T
    visited = torch.full((cap,), SENTINEL, dtype=torch.int64, device=device)
    visited[0] = _hash(x0, hash_vec)
    visited = torch.sort(visited).values
    temps = torch.linspace(temperature, temp_end, T, device=device)

    for t in range(T):
        logits, value = _forward(model, states, chunk)
        scores = torch.log_softmax(logits, dim=-1) + alpha * value[:, None]
        if float(temps[t]) != 0.0:
            u = torch.rand(scores.shape, generator=generator, device=device).clamp(1e-6, 1 - 1e-6)
            scores = scores + temps[t] * (-torch.log(-torch.log(u)))
        scores = torch.where(alive[:, None], scores, torch.full_like(scores, neg_inf))

        top_vals, top_idx = torch.topk((cum[:, None] + scores).reshape(-1), B)
        parent = torch.div(top_idx, n_actions, rounding_mode="floor")
        flat_action = top_idx % n_actions

        parent_states = states[parent]
        i, r, k1, k2 = decode_action(flat_action, L)
        new_states = s_move(parent_states, i, r, k1, k2, L)

        seqs = seqs[parent]
        seqs[:, t] = flat_action

        nnz = (new_states != 0).sum(-1)
        terminated_raw = nnz == n_gen
        dones = terminated_raw | (t + 1 >= T)
        noop = (parent_states == new_states).all(-1)
        parent_alive = alive[parent]
        terminated = terminated_raw & parent_alive

        alive = parent_alive & ~dones & (top_vals > -1e30) & ~noop
        cum = torch.where(alive, top_vals, torch.full_like(top_vals, neg_inf))

        # Within-step dedup: keep the highest-cumlp beam per distinct state.
        h = _hash(new_states, hash_vec)
        o1 = torch.argsort(-cum, stable=True)
        order = o1[torch.argsort(h[o1], stable=True)]
        sorted_h = h[order]
        is_first = torch.cat([torch.ones(1, dtype=torch.bool, device=device),
                              sorted_h[1:] != sorted_h[:-1]])
        keep = torch.zeros(B, dtype=torch.bool, device=device)
        keep[order] = is_first
        alive &= keep

        # Global visited check, then append the survivors.
        pos = torch.searchsorted(visited, h).clamp(max=cap - 1)
        alive &= ~(visited[pos] == h)
        cum = torch.where(alive, cum, torch.full_like(cum, neg_inf))
        entries = torch.where(alive, h, torch.full_like(h, SENTINEL))
        visited = torch.sort(torch.cat([visited, entries])).values[:cap]

        states = new_states
        if bool(terminated.any()):
            beam_idx = int(torch.nonzero(terminated)[0])
            return True, t + 1, seqs[beam_idx, :t + 1].cpu().tolist()

    return False, -1, []


def decode_path(flat_actions, max_length=24):
    """flat action -> `[i, r, k1, k2]`, the Definition 2.1 move the env applies."""
    t = torch.as_tensor(flat_actions, dtype=torch.int64)
    if t.numel() == 0:
        return []
    i, r, k1, k2 = decode_action(t, max_length)
    return [[int(a), int(b), int(c), int(d)] for a, b, c, d in zip(i, r, k1, k2)]


def repair_jsonl(path, progress=print):
    """Drop a half-written trailing line, returning the bytes removed.

    Rows are appended as `json.dumps(row) + "\\n"` and fsynced, so a killed
    process can only damage the LAST line. This must run *before* anything opens
    the file for append: left in place the stub has no newline, so the next row
    is concatenated onto it and a recoverable truncated-final line becomes a
    corrupt interior line that no later read can undo. Tolerating it at read
    time (`_done_indices` does) is not enough -- the row appended onto the stub
    is then permanently unreadable and its presentation is re-run forever.

    Truncating back to the last newline can discard one complete row whose
    newline was lost. That is deliberate: the row is simply absent from `done`
    and gets re-decoded.
    """
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return 0
    with open(path, "rb+") as f:
        f.seek(-1, os.SEEK_END)
        if f.read(1) == b"\n":
            return 0
        size = f.tell()
        keep = size
        while keep > 0:
            f.seek(keep - 1)
            if f.read(1) == b"\n":
                break
            keep -= 1
        f.truncate(keep)
    progress(f"    repaired {os.path.basename(path)}: dropped a {size - keep}-byte "
             f"truncated final line; that presentation will be re-decoded")
    return size - keep


def _done_indices(path):
    done = set()
    if not os.path.exists(path):
        return done
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                done.add(int(json.loads(line)["presentation_idx"]))
            except (ValueError, KeyError):
                continue                              # torn trailing line
    return done


def run_beam(model, presentations, out_path, *, start=0, end=None, device="cpu",
             beam_width=1024, max_steps=150, alpha=0.0, temperature=0.0, temp_end=0.0,
             max_length=24, n_gen=2, seed=0, chunk=4096, heartbeat_s=60.0,
             time_budget_s=None, resume=True, progress=print):
    """Decode `presentations[start:end]`, appending one jsonl row each.

    `presentations` is `(S, 2 * max_length)`; rows are indexed by their position
    in the *evaluation* file, which is what the paper's denominator counts.

    `time_budget_s` stops the loop **between** presentations once the budget is
    spent. It is a wall-clock bound, not a search bound: every row already
    written is a complete, full-width decode, and the next call resumes at the
    first presentation missing from the file. That is what makes a fixed-length
    smoke run meaningful -- it measures the real per-presentation cost at
    production settings instead of a shrunken proxy, and its rows are kept.
    """
    device = torch.device(device)
    end = len(presentations) if end is None else end
    states = torch.as_tensor(np.asarray(presentations), dtype=torch.int64, device=device)
    hash_vec = make_hash_vec(states.shape[1], device)
    gen = torch.Generator(device=device)
    gen.manual_seed(seed)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    repair_jsonl(out_path, progress)          # before any append, never gated on resume
    already = _done_indices(out_path) if resume else set()
    todo = [p for p in range(start, end) if p not in already]
    progress(f"beam: {len(todo)} presentations to run "
             f"({len(already)} already in {os.path.basename(out_path)}), "
             f"width={beam_width} T={max_steps} alpha={alpha}")

    t0 = last_beat = time.time()
    n_solved = 0
    n_done = 0
    stopped_early = False
    with open(out_path, "a") as fh:
        for n, p_idx in enumerate(todo, 1):
            t_row = time.time()
            solved, plen, path = beam_search_one(
                model, states[p_idx], hash_vec, n_gen=n_gen, max_length=max_length,
                beam_width=beam_width, max_steps=max_steps, alpha=alpha,
                temperature=temperature, temp_end=temp_end, generator=gen, chunk=chunk)
            n_solved += int(solved)
            fh.write(json.dumps({
                "presentation_idx": p_idx,
                "solved": bool(solved),
                "path_length": int(plen),
                "path": [int(a) for a in path],
                "path_decoded": decode_path(path, max_length),
                "beam_width": beam_width,
                "max_steps": max_steps,
                "alpha": alpha,
                "seconds": round(time.time() - t_row, 3),
            }) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
            n_done = n

            now = time.time()
            if now - last_beat >= heartbeat_s or n == len(todo):
                rate = n / max(now - t0, 1e-9)
                eta = (len(todo) - n) / max(rate, 1e-9)
                progress(f"  [{n}/{len(todo)}] solved={n_solved} "
                         f"{rate * 60:.1f} pres/min  ETA {eta / 60:.1f} min")
                last_beat = now

            if time_budget_s and now - t0 >= float(time_budget_s):
                stopped_early = n < len(todo)
                if stopped_early:
                    rate = n / max(now - t0, 1e-9)
                    progress(f"  time budget {time_budget_s:.0f}s spent after {n} "
                             f"presentations ({rate * 60:.1f} pres/min); stopping. "
                             f"The rows written are complete -- rerun to continue "
                             f"from presentation {todo[n]}.")
                break
    return {"attempted": n_done, "solved": n_solved, "out": out_path,
            "remaining": len(todo) - n_done, "stopped_early": stopped_early,
            "elapsed_s": round(time.time() - t0, 1)}


def summarise(out_path):
    rows = []
    with open(out_path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    continue
    solved = [r for r in rows if r["solved"]]
    return {
        "rows": len(rows),
        "solved": len(solved),
        "mean_path_length": float(np.mean([r["path_length"] for r in solved])) if solved else float("nan"),
    }
