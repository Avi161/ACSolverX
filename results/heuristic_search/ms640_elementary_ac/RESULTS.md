# MS640 elementary AC certificates

`ms640.elementary.jsonl` converts all 640 saved mixed cascade certificates into
ordinary generator-level AC operations. Each output row identifies its source
by presentation ID and the SHA-256 of the complete source JSONL.

The compact move encoding is:

- `["I", target]`: invert relator `target`.
- `["S"]`: swap the two relators.
- `["C", target, letter]`: conjugate relator `target` by one letter in
  `x`, `X`, `y`, `Y`.
- `["M", target, source]`: right-multiply relator `target` by the other
  relator.

The conversion is deterministic algebra and performs no presentation search.
It transports substitution conjugators through the inverse cumulative basis
change, emits every cyclic canonicalization explicitly, and Nielsen-reduces the
terminal basis. Every row was replayed from its original input to exactly
`["x", "y"]`.

Run:

```console
python -m experiments.search.decode_ac_jsonl SOURCE.jsonl OUTPUT.jsonl
```

The input may use mixed `states`/`steps` records or compact-search
`path`/`path_moves` records.

## Measured full conversion

- Source rows: 640 solved out of 640.
- Source SHA-256: `901b4c62b7afa380b3e435a3e160b43832283372ad744bf7bfcec737a4d13c0f`.
- Output SHA-256: `2e3d65882dbf107b6d0689db213b7df879a4214298bd418490bf3376c37da61c`.
- Conversion and built-in replay: 6.45 s wall, 5.75 s CPU, one thread.
- Separate replay of the written JSONL: 1.83 s wall, 1.47 s CPU.
- Strict elementary moves: 2,388,332 total; median 226; mean 3,731.77;
  maximum 159,704 on `ms637`.
- Output size: 28,785,317 bytes.

The previously measured fixed-cascade search itself took 2.356716 s wall for
all 640 rows. Combining that search measurement with this conversion gives
8.81 s wall, but the two timings are separate passes rather than one matched
end-to-end timing.
