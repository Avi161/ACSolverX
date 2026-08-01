# Git checkpoints and pushes

Keep coherent verified work checkpointed; inspect status and staged scope before committing. Before every push, append a new headed section to `logs/DD-MM-YYYY.md` using `## HH:MM:SS UTC · \`<shortsha>\`` and one to three linked sentences. Commit the log body with the work (or immediately after), then make a follow-up commit that replaces the placeholder with the short SHA of the body-carrying commit. Do not amend to chase a self-hash.

Push only after the headed log section is present and bound to its body commit. Preserve the exact commit on a transient push failure; verify ahead state and retry without rewriting history or broadening the staged scope.
