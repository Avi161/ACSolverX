# Aut(F₂) orbit canonical form (Whitehead)

Decide whether two 2-generator presentations are the **same up to automorphism of the free group F₂**.

This is Whitehead’s algorithm for pairs of cyclically reduced words in `⟨x, y⟩`:

1. **Peak-reduce** — apply length-changing Whitehead automorphisms until total length `|r1|+|r2|` cannot drop.
2. **Minimal level set** — explore Aut-images that keep that minimal total length.
3. **Lex-min** — among those, take the lexicographically smallest pair under the solver’s letter order `Y < y < X < x`.

Two presentations lie in the same Aut(F₂) orbit **iff** their canonical representatives are equal.

## Files (stdlib only)

| file | role |
|---|---|
| `autcanon.py` | Whitehead pipeline + witnessing automorphism `φ` |
| `words.py` | word algebra (`apply_hom`, `canon_pair`, `cyc_reduce`, …) |
| `__init__.py` (+ parents) | package markers so imports work |

No numpy, numba, or JAX.

## Alphabet

Relators are strings over `x`, `X`, `y`, `Y` (inverse = swapcase). Example: `"YXYxyx"`.

## How to run

From the **repo root** (so `experiments` is importable):

```bash
python3 - <<'EOF'
from experiments.equivalence_classes.lib.autcanon import aut_canon, check

P  = ("YYYYXyyyx", "YYXYxYx")
P2 = ("XXXXXXYxxxyxx", "YXXYxyxx")   # Aut-equivalent rewriting of P
P3 = ("YXYxyx", "YYYYxxx")          # different orbit (AK(3))

_, rep1, phi1 = aut_canon(P)
_, rep2, _    = aut_canon(P2)
_, rep3, _    = aut_canon(P3)

print("rep(P)  =", rep1)
print("rep(P2) =", rep2)
print("same orbit P ~ P2?", rep1 == rep2)   # True
print("same orbit P ~ P3?", rep1 == rep3)   # False

# Optional certificate: φ maps P onto the representative by substitution alone
assert check(P, rep1, phi1)
print("witness φ:", {k: phi1[k] for k in ("x", "y")})
EOF
```

With the project venv (if present):

```bash
.venv/bin/python3 -c "from experiments.equivalence_classes.lib.autcanon import aut_canon; print(aut_canon(('YXYxyx','YYYYxxx'))[1])"
```

## Return value

`aut_canon(pair)` → `(total, rep, phi)` where

- `total` — Aut-minimal total length `|r1|+|r2|`
- `rep` — canonical pair `(r1*, r2*)` (the orbit ID)
- `phi` — dict `{"x": word, "y": word}` with `canon_pair(φ(P)) == rep`

## Cost

On typical AC presentations of total length ~15, one call is about **1–5 ms**. A safety `level_cap=50000` stops exploring if the minimal level set is huge; if that fires, the returned `rep` can be incomplete.

## What this does *not* do

- It does **not** run Andrews–Curtis / greedy search.
- It does **not** decide AC-triviality; it only names the Aut(F₂) orbit.
- Equal reps ⇒ same problem up to change of basis; unequal reps ⇒ not related by any Aut(F₂) map.
