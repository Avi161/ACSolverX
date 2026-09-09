# Experimental elementary-certificate compression

`certificate_compress.compress` replaces each maximal unary block between
multiply moves by a normal form. Relative to the pair at the preceding
multiply boundary, target `i` is stored as

```text
c_i^-1 r_perm(i)^sign_i c_i.
```

A swap permutes the two triples, inversion flips one sign, and conjugation by
`d` appends `d` to `c_i`. Conjugators are maintained as signed-letter stacks,
so free cancellation is linear in the input conjugator length. At a multiply
boundary the compressor emits at most one swap, then the needed target
inversions and freely reduced conjugator letters, followed by the unchanged
multiply. This realizes the stored triples exactly. Induction over multiply
boundaries proves that the original and compressed pairs agree at every such
boundary and at the endpoint.

The emitted unary cost cannot increase: swaps cancel by parity, inversions by
parity, and each stored conjugator is the free reduction of the original
concatenation. Input conjugation records may contain whole words, so this is a
weighted elementary-cost statement; the number of Python records can increase
for such non-unit records.

The focused check independently replays 200 short planted blocks and compares
all multiply boundaries. It also tests three small saved certificates:

| presentation | original | compressed | reduction |
|---|---:|---:|---:|
| `ac19_2276` | 497 | 435 | 12.5% |
| `ac19_2094` | 254 | 228 | 10.2% |
| `ac19_9934` | 491 | 429 | 12.6% |

Each saved endpoint remains `(x,y)`, and compression took under 0.4 ms per
certificate in this small local sample. This table records the initial optional postprocessing experiment; no
full-corpus performance claim follows from these three selected certificates.
The same invariant is now implemented during emission by
`certificate_decoder_compact_moves.py`, which the full AC19 census runner uses.
See `AC19_FULL_CENSUS_ALGORITHM.md` for that run and its separate timings.
