"""One-time conversion of a flax/orbax ``params`` checkpoint to a torch ``state_dict``.

Port of ``origin/experiments/ppo:experiments/ppo/transplant.py`` (tip c73b11f2). Needs ``jax`` and
``orbax-checkpoint`` (not part of the extra); the shipped ``checkpoint/610model_1000.pt`` was made with::

    git archive origin/main ppo_checkpoints/610model/1000 | tar -x -C /tmp/ck
    python -m acx.rl.convert /tmp/ck/ppo_checkpoints/610model/1000 acx/rl/checkpoint/610model_1000.pt

The checkpoint was written on ROCm; arrays are therefore restored as plain numpy, which never
consults the device sharding. flax kernels are ``(in, out)`` (torch ``(out, in)``, transposed),
LayerNorm ``scale`` is torch's ``weight``; every one of the 95 arrays must map (no silent skips).
"""
import argparse
import os

import numpy as np
import torch

LEAVES = {"kernel": ("weight", True), "scale": ("weight", False), "bias": ("bias", False)}


def name_map(layers=2):
    """flax module path -> torch module path."""
    m = {f"Dense_{k}": n for k, n in enumerate(("critic0", "critic1", "critic2", "actor0", "actor1"))}
    for b in range(layers):
        f, t = f"RelativeDualRingBlock_{b}", f"blocks.{b}"
        m.update({f"{f}.LayerNorm_{i}": f"{t}.ln{i}" for i in range(6)})
        m.update({f"{f}.Dense_{j}": f"{t}.{n}" for j, n in enumerate(("mlp0_in", "mlp0_out", "mlp1_in", "mlp1_out"))})
        for s in range(2):
            sa, ca = f"{f}.RelativeSelfAttention_{s}", f"{f}.RelativeCrossAttention_{s}"
            m.update({f"{sa}.Dense_0": f"{t}.sa{s}.qkv", f"{sa}.Dense_1": f"{t}.sa{s}.out",
                      f"{ca}.Dense_0": f"{t}.ca{s}.q", f"{ca}.Dense_1": f"{t}.ca{s}.kv", f"{ca}.Dense_2": f"{t}.ca{s}.out"})
    return m


def to_state_dict(flat, layers=2):
    """Flat ``{"Dense_0.kernel": array}`` -> torch ``state_dict``; raises on any unmapped array."""
    names, sd = name_map(layers), {}
    for key, arr in flat.items():
        arr = torch.from_numpy(np.asarray(arr, dtype=np.float32).copy())
        base, leaf = key.rsplit(".", 1)
        if key == "shared_embed.embedding":
            sd["embed.weight"] = arr
        elif leaf == "rel_emb":
            sd[f"{names[base + '.Dense_0'].rsplit('.', 1)[0]}.rel_emb"] = arr
        elif base in names and leaf in LEAVES:
            suffix, transpose = LEAVES[leaf]
            sd[f"{names[base]}.{suffix}"] = arr.t().contiguous() if transpose else arr
        else:
            raise KeyError(f"unmapped checkpoint array {key!r}")
    return sd


def read_orbax(step_dir):
    """Flat numpy dict of the ``params`` item of an orbax step directory."""
    import orbax.checkpoint as ocp

    def meta_tree(md):
        for get in (lambda m: m.item_metadata.tree, lambda m: m.item_metadata, lambda m: m):
            try:
                t = get(md)
            except AttributeError:
                continue
            if isinstance(t, dict):
                return t

    def walk(t, f, prefix=""):                       # nested dict -> flat dotted dict of f(leaf)
        out = {}
        for k, v in t.items():
            out.update(walk(v, f, f"{prefix}{k}.") if isinstance(v, dict) else {prefix + k: f(v)})
        return out

    def rebuild(t):                                   # nested dict with every leaf a numpy request
        return {k: rebuild(v) if isinstance(v, dict) else ocp.RestoreArgs(restore_type=np.ndarray) for k, v in t.items()}

    ckptr, path = ocp.PyTreeCheckpointer(), os.path.join(os.path.abspath(step_dir), "params")
    tree = ckptr.restore(path, restore_args=rebuild(meta_tree(ckptr.metadata(path))))
    return walk(tree.get("params", tree), np.asarray)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("step_dir")
    ap.add_argument("out")
    a = ap.parse_args()
    sd = to_state_dict(read_orbax(a.step_dir))
    torch.save(sd, a.out)
    print(f"wrote {a.out}: {len(sd)} tensors")
