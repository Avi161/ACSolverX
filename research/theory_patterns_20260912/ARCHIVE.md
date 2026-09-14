# Large generated artifact

`prepared_frames_full124.jsonl.gz` is a deterministic, lossless gzip archive of
the 124-row prepared-frame JSONL. Its decompressed SHA-256 is
`cc94455b764e8183a8b606afdbe94d8940ca0944021a4a4d93e8b84b56ac7abe`,
the hash recorded by downstream result files. The uncompressed file is about
252 MB and exceeds GitHub's per-file limit; the archive is about 4.4 MB.

The producer writes this gzip form directly. Downstream readers stream it and
continue to use `prepared_frames_full124.jsonl` as the logical provenance name,
so existing line pointers and decompressed content hashes remain valid.
