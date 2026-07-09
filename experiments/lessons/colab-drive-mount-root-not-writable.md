# [2026-07-08] Colab Drive path — mount root is not writable [TRAP]
`os.makedirs("/content/drive/acsolverx_results")` → `OSError [Errno 95] Operation not supported`. The Drive FUSE mount root `/content/drive/` rejects directory creation. **Rule:** all Drive output paths must be under `/content/drive/MyDrive/...` (or a Shared drive), never `/content/drive/` directly.
