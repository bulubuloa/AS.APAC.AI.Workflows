# How to use the shared knowledge (Codex)

Codex does not load project memory automatically, so do it explicitly:
- **At the start of a session**, read `ai-workspace/memory/OmnicasaAS/MEMORY.md` (the index) and, when working inside a repo, the repo's index (`ai-workspace/memory/ABCB/MEMORY.md`, `…/ABMB/MEMORY.md`). Open the notes the index points at when they are relevant to the ticket — they hold environment ids, drifted stored procedures, pipeline quirks and incidents that are not derivable from the code.
- **At the end of a ticket**, write what you learned that is non-obvious as a new note in the same folder (one fact per file, front-matter `name`/`description`/`metadata.type`), add a one-line pointer to `MEMORY.md`, and tell the developer to commit `ai-workspace/`.
- Task files live in `ai-workspace/issues/ABE-xxxx.md` (symlinked as `issues/`). The workflow prompts are `/prompts:task-fetch` and `/prompts:task-analyse`.

