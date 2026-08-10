"""Move `ppo_checkpoints/<name>/<step>/params` (flax/orbax) into the torch module.

This is the strongest correctness test available for `policy.py` and it costs no
training: load the shipped weights into both frameworks and require the logits
and the value to agree. If they do, the port is right.

Restoring is **params-only and target-free**. `beam/beam_search.py` restores
`solve_data` alongside them, sized from the current line count of the training
file -- and `610model`'s arrays are 157,217 long while `data/AC19_extended.txt`
is 156,762 lines today, so that path raises a shape error on this checkpoint.
Nothing here needs `solve_data`, so nothing here asks for it.

`export_npz` converts once (on a machine that has orbax) into a plain `.npz`, so
the parity fixture and every later load are a numpy read with no JAX in sight.
"""

import json
import os

import numpy as np
import torch

_L = 24


def _flatten(tree, prefix=""):
    out = {}
    for k, v in tree.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(_flatten(v, key + "."))
        else:
            out[key] = np.asarray(v)
    return out


def read_orbax_params(ckpt_dir, step=None):
    """Flat `{"Dense_0.kernel": array, ...}` from an orbax params item."""
    import orbax.checkpoint as ocp

    ckpt_dir = os.path.abspath(ckpt_dir)
    if step is None:
        steps = sorted(int(d) for d in os.listdir(ckpt_dir) if d.isdigit())
        if not steps:
            raise SystemExit(f"no checkpoint steps under {ckpt_dir}")
        step = steps[-1]
    path = os.path.join(ckpt_dir, str(step), "params")
    tree = ocp.PyTreeCheckpointer().restore(path)
    if isinstance(tree, dict) and set(tree) == {"params"}:
        tree = tree["params"]
    return _flatten(tree), step


def read_config(ckpt_dir, step):
    """The `JsonSave` config item, readable without orbax."""
    with open(os.path.join(ckpt_dir, str(step), "config", "metadata")) as fh:
        return json.load(fh)


def export_npz(ckpt_dir, out_path, step=None):
    flat, step = read_orbax_params(ckpt_dir, step)
    np.savez(out_path, **flat)
    print(f"wrote {out_path}: {len(flat)} arrays from step {step}")
    return out_path


def _pairs(num_layers=2):
    """flax dotted name -> (torch module prefix, is_kernel) for every parameter."""
    m = {
        "shared_embed.embedding": ("embed.weight", False),
        "Dense_0": ("critic0", True), "Dense_1": ("critic1", True), "Dense_2": ("critic2", True),
        "Dense_3": ("actor0", True), "Dense_4": ("actor1", True),
    }
    for n in range(num_layers):
        b = f"RelativeDualRingBlock_{n}"
        t = f"blocks.{n}"
        for i in range(6):
            m[f"{b}.LayerNorm_{i}"] = (f"{t}.ln{i}", False)
        for s in range(2):
            m[f"{b}.RelativeSelfAttention_{s}.Dense_0"] = (f"{t}.sa{s}.qkv", True)
            m[f"{b}.RelativeSelfAttention_{s}.Dense_1"] = (f"{t}.sa{s}.out", True)
            m[f"{b}.RelativeSelfAttention_{s}.rel_emb"] = (f"{t}.sa{s}.rel_emb", False)
            m[f"{b}.RelativeCrossAttention_{s}.Dense_0"] = (f"{t}.ca{s}.q", True)
            m[f"{b}.RelativeCrossAttention_{s}.Dense_1"] = (f"{t}.ca{s}.kv", True)
            m[f"{b}.RelativeCrossAttention_{s}.Dense_2"] = (f"{t}.ca{s}.out", True)
        for j, name in enumerate(("mlp0_in", "mlp0_out", "mlp1_in", "mlp1_out")):
            m[f"{b}.Dense_{j}"] = (f"{t}.{name}", True)
    return m


def flat_to_state_dict(flat, num_layers=2):
    """flax params -> a torch `state_dict` for `RelativeDualRingActorCritic`.

    flax kernels are `(in, out)`; torch `Linear.weight` is `(out, in)`, hence the
    transpose. LayerNorm's `scale` is torch's `weight`. `rel_emb` and the
    embedding table need no reshaping.
    """
    mapping = _pairs(num_layers)
    sd, seen = {}, set()
    for name, arr in flat.items():
        arr = np.asarray(arr, dtype=np.float32)
        if name in mapping:                                   # rel_emb, embedding
            sd[mapping[name][0]] = torch.from_numpy(arr)
            seen.add(name)
            continue
        base, _, leaf = name.rpartition(".")
        if base not in mapping:
            raise KeyError(f"unmapped checkpoint parameter {name!r}")
        prefix, is_kernel = mapping[base]
        if leaf == "kernel":
            sd[f"{prefix}.weight"] = torch.from_numpy(arr.T.copy())
        elif leaf == "scale":
            sd[f"{prefix}.weight"] = torch.from_numpy(arr)
        elif leaf == "bias":
            sd[f"{prefix}.bias"] = torch.from_numpy(arr)
        else:
            raise KeyError(f"unmapped checkpoint leaf {name!r}")
        seen.add(name)
    missing = set(flat) - seen
    if missing:
        raise KeyError(f"checkpoint parameters not transplanted: {sorted(missing)}")
    return sd


def load_into(model, source, step=None):
    """`source` is either a `.npz` written by `export_npz` or a checkpoint dir."""
    if str(source).endswith(".npz"):
        with np.load(source) as z:
            flat = {k: z[k] for k in z.files}
    else:
        flat, _ = read_orbax_params(source, step)
    sd = flat_to_state_dict(flat, num_layers=len(model.blocks))
    incompatible = model.load_state_dict(sd, strict=False)
    unexpected = [k for k in incompatible.unexpected_keys]
    real_missing = [k for k in incompatible.missing_keys if not k.endswith("base_rel_dist")]
    if unexpected or real_missing:
        raise KeyError(f"state_dict mismatch: missing={real_missing} unexpected={unexpected}")
    return model


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("ckpt_dir", help="e.g. ppo_checkpoints/610model")
    p.add_argument("out_npz")
    p.add_argument("--step", type=int, default=None)
    a = p.parse_args()
    export_npz(a.ckpt_dir, a.out_npz, a.step)
