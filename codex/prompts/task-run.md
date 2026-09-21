---
description: Run a ticket end to end — fetch → analyse → implement → verify → deliver — with pauses for the human (default), or --auto / --cowork.
argument-hint: <jira-key> [--auto | --cowork]
---

Run the whole loop for ticket $ARGUMENTS by following the command files in this folder in order. Read each file and execute it; do not skip its rules.

Modes:
- **default** — pause after `/prompts:task-fetch` (developer reviews the task file) and after `/prompts:task-analyse` (developer reads the analysis and answers open questions). Use `AskUserQuestion` at each pause with "continue / change / stop".
- **`--cowork`** — as default, plus pause before every commit (show `git diff --stat`, proposed message) and before `/prompts:task-deliver` posts anything.
- **`--auto`** — no pauses, no questions. Decide, record every decision, stop only on a true blocker (refused permission you cannot route around, missing access, contradictory ticket). Never use `--auto` for tickets that touch production data or payments logic.

Sequence: `task-fetch.md` → `task-analyse.md` → `task-implement.md` → `task-verify.md` → `task-deliver.md`, each appending its section to `issues/$ARGUMENTS.md`. At the end post one summary: branches and commits, evidence table, what the developer still has to do (push, PR, scripts, answers), and the memory notes written.
