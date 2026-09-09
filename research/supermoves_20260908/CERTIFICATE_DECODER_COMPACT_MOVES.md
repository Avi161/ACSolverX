# Streaming compressed elementary decoder

`certificate_decoder_compact_moves.py` reuses the trusted fast decoder's exact
code object and globals, substituting only `_CompactTrace` through a private
globals copy. It does not mutate the original module and is safe to call beside
the original decoder.

The trace updates and validates its concrete pair exactly as `_ElementaryTrace`
does. Its output side retains one unary transformation per target as
`(permutation, sign, freely reduced conjugator stack)`. Whole-word calls to
`conjugate_word` feed the word directly into the stack. A multiply flushes the
minimal unary normal form and then emits the unchanged multiply; final access
flushes the last block. The proof is the same multiply-boundary invariant in
`CERTIFICATE_COMPRESS.md`.

On the three prescribed saved certificates, streaming output equals
`certificate_compress.compress(fast_decode(...))` record for record and
independently replays to `(x,y)`:

| presentation | original | streaming | warm fast CPU | streaming CPU |
|---|---:|---:|---:|---:|
| `ac19_11767` | 6,864 | 3,130 | 9.39 ms | 14.86 ms |
| `ac19_2574` | 14,672 | 8,076 | 12.50 ms | 11.20 ms |
| `ac19_63607` | 14,609 | 8,013 | 14.11 ms | 11.47 ms |

These are three serial local timings after warming both decoders. The first is
slower and the other two are modestly faster, so this small sample supports the
certificate-size reduction but not a uniform decode-time improvement. This was the initial three-row experiment. The completed AC19 census uses this
streaming decoder through `run_full_ac19_final1k.py`, with independent replay
for every solve; see `AC19_FULL_CENSUS_ALGORITHM.md` and the census results.
