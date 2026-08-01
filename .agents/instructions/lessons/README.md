# Historical lesson protocol

Historical lessons are partitioned by heading date. Arbitrary Markdown in this directory is not auto-discovered. First search by topic, then read only the matching complete lesson blocks:

```sh
rg -n '<topic>' .agents/instructions/lessons
```

Do not summarize, rewrite, deduplicate, or move existing lesson blocks while using them. Add a new lesson only to the file for its current date, preserving the block form `### YYYY-MM-DD ...`.
