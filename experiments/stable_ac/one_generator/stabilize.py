"""Phase 1 — `z = w(x,y)` stabilization: 2-generator presentation -> 3-generator.

Add a generator `z` *defined as a word* `z = w(x,y)`:
    <x,y | r1, r2>  ->  <x,y,z | r1, r2, z·w^-1>
The new z-relator `z·w^-1 = [z] ++ inverse(w)` shares w's x/y letters with r1/r2, so the
n-relator substitution search can swap `w <-> z` directly (that content is exactly why a
non-trivial `z=w` is not the discarded trivial `z`; see PLAN Background).

Encoding = the env's signed-int convention: x->1, y->2, z->3, inverses negative, 0 = pad.
A presentation is a flat list `n_gen * L` (each relator L=24, zero-padded). Baseline words
`w in {x, y, r1, r2}` (dumbest first). Every z-relator is `1 + |w| <= 18 <= L`, so L=24 holds
for all baseline words on both MS(1190) and the 261 reps — no length bump needed.

Pure Python (no numba/JAX): runs once over <=1190 lines. `python stabilize.py` validates and
writes all datasets under data/stabilized/.
"""
import argparse
import ast
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
L = 24
OLD_N_GEN = 2
NEW_N_GEN = 3
WORDS = ("x", "y", "r1", "r2")
PRESET = {"x": [1], "y": [2]}


# ---- word ops (int lists over ±1..±n_gen) ----------------------------------

def inverse(w):
    return [-a for a in reversed(w)]


def free_reduce(w):
    out = []
    for a in w:
        if out and out[-1] == -a:
            out.pop()
        else:
            out.append(a)
    return out


def cyclic_reduce(w):
    w = free_reduce(w)
    i, j = 0, len(w) - 1
    while i < j and w[i] == -w[j]:
        i += 1
        j -= 1
    return w[i:j + 1]


# ---- flat <-> relators (n-relator-generic; no //2) -------------------------

def flat_to_relators(flat, n_gen, half=L):
    """Split a flat presentation into `n_gen` relators, stripping zero padding
    (0 is only ever padding — letters are ±1..±n_gen, never 0)."""
    return [[a for a in flat[g * half:(g + 1) * half] if a != 0] for g in range(n_gen)]


def relators_to_flat(rels, n_gen, half=L):
    flat = []
    for g in range(n_gen):
        rel = rels[g]
        if len(rel) > half:
            raise ValueError(f"relator {g} length {len(rel)} > cap {half}: {rel}")
        flat.extend(list(rel) + [0] * (half - len(rel)))
    return flat


# ---- the stabilization -----------------------------------------------------

def z_word_for(spec, r1, r2):
    if spec == "r1":
        return list(r1)
    if spec == "r2":
        return list(r2)
    return list(PRESET[spec])


def stabilize_flat(flat, z_spec, old_n_gen=OLD_N_GEN, new_n_gen=NEW_N_GEN, half=L):
    """flat (len old_n_gen*half) -> flat (len new_n_gen*half) with appended z-relator z·w^-1."""
    rels = flat_to_relators(flat, old_n_gen, half)
    w = z_word_for(z_spec, rels[0], rels[1])
    k = new_n_gen                                   # new generator id (x=1,y=2,z=3)
    z_relator = cyclic_reduce([k] + inverse(w))
    return relators_to_flat(rels + [z_relator], new_n_gen, half)


def decode_z_word(z_relator, k):
    """Inverse of the transform: drop the leading z=k, invert the rest -> w (up to reduction)."""
    if not z_relator or z_relator[0] != k:
        raise ValueError(f"z-relator does not start with z={k}: {z_relator}")
    return inverse(z_relator[1:])


# ---- dataset writer + validation -------------------------------------------

def _read_flats(in_path):
    with open(in_path) as f:
        return [ast.literal_eval(line) for line in f if line.strip()]


def validate(in_flats, stab_flats, z_spec, old_n_gen=OLD_N_GEN, new_n_gen=NEW_N_GEN, half=L):
    """Round-trip + invariance checks. Returns (max z-relator length) or raises."""
    k, max_z = new_n_gen, 0
    for flat, sflat in zip(in_flats, stab_flats):
        assert len(sflat) == new_n_gen * half, f"bad length {len(sflat)}"
        assert sflat[:old_n_gen * half] == flat, "r1/r2 prefix changed"
        rels = flat_to_relators(sflat, new_n_gen, half)
        w = z_word_for(z_spec, *flat_to_relators(flat, old_n_gen, half))
        assert cyclic_reduce(decode_z_word(rels[-1], k)) == cyclic_reduce(w), "z decodes wrong"
        assert relators_to_flat(rels, new_n_gen, half) == sflat, "flat<->relators not identity"
        max_z = max(max_z, len(rels[-1]))
    return max_z


def write_stabilized_dataset(in_path, z_spec, out_path, old_n_gen=OLD_N_GEN,
                             new_n_gen=NEW_N_GEN, half=L):
    in_flats = _read_flats(in_path)
    stab = [stabilize_flat(f, z_spec, old_n_gen, new_n_gen, half) for f in in_flats]
    max_z = validate(in_flats, stab, z_spec, old_n_gen, new_n_gen, half)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        for v in stab:
            f.write(str(v) + "\n")
    return len(stab), max_z


# stem -> (input path, output basename prefix)
DATASETS = {
    "1190MS": os.path.join(ROOT, "data", "1190MS.txt"),
    "ms_reps_unsolved": os.path.join(ROOT, "data", "ms_unsolved_reps", "ms_reps_unsolved.txt"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_dir", default=os.path.join(ROOT, "data", "stabilized"))
    args = ap.parse_args()

    print(f"L={L}  words={WORDS}  -> {os.path.relpath(args.out_dir, ROOT)}/\n")
    for stem, in_path in DATASETS.items():
        for w in WORDS:
            out = os.path.join(args.out_dir, f"{stem}_z_{w}.txt")
            n, max_z = write_stabilized_dataset(in_path, w, out)
            flag = "" if max_z <= L else f"  !! max_z {max_z} > L {L}"
            print(f"  {stem:16} z={w:2} -> {n:5} lines, max z-relator = {max_z:2}{flag}  "
                  f"[{os.path.relpath(out, ROOT)}]")
    print("\nOK: all datasets validated (length 3L, r1/r2 unchanged, z decodes to w, round-trip identity).")


if __name__ == "__main__":
    main()
