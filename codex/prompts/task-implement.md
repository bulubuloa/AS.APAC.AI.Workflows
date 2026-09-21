---
description: Implement the plan in a task file — right base branch, code, build, tests, commits. No push.
argument-hint: <path-to-task-file> [--auto]
---

Implement the task in $ARGUMENTS following its `## Analysis → Plan`. Stop at committed branches; pushing, PRs and shared-environment writes are the developer's (see `/prompts:task-deliver`).

## Rules
- The task file must contain a `## Analysis` with a Plan. If it does not, stop and say to run `/prompts:task-analyse` first.
- Without `--auto`: if the Analysis lists open questions that change the implementation, ask them once with `AskUserQuestion` (1–3 questions), then implement without further questions. With `--auto`: decide yourself, record every decision under `Decisions` in the task file and in the PR body later.
- Follow the repo's `CLAUDE.md` and the workspace conventions: match existing patterns, one-line "why" comments with the ticket id inline, no new abstractions without a reason.
- Never write to SIT/UAT/PROD databases, Secrets Manager, SSM or IAM here. Scripts that must run there are written to `database/Sprint<N>/` (idempotent, header with env order, drift notes, rollback) or to `issues/<KEY>-scripts/` and listed for the developer.

## Step 1 — Branch, from the right base
For each repo the plan touches: base branch = the one that feeds the **first test environment** (workspace `CLAUDE.md` table — `develop` for ABCB ClientService.API / ABVB / ABF; `roadside_release_sit` or the release branch for ABMB; `data-processer-pre-production` for DataProcesser). `git fetch origin <base>`; branch `jira/<KEY>-<short-slug>` from `origin/<base>`; if the branch exists, reuse it and note how far behind base it is.

## Step 2 — Stored procedures and schema (if the plan touches them)
`SHOW CREATE PROCEDURE` / `SHOW CREATE TABLE` on SIT, UAT and PROD (read-only) and diff against the repo script before editing. Base the new script on the environment version that is meant to be live and document every difference in the script header. Additive schema only.

## Step 3 — Code
Implement the plan in the order it gives. Build after each repo (`dotnet build <proj>`, `npm run build`); run the tests for the touched area (`dotnet test`). Fix what you broke; do not edit a test to make it pass — that is a finding.

## Step 4 — Commit
Stage only the files you changed (never `git add -A`; never data files, dumps, screenshots, `.codex/`, `.claude/`). One commit per repo per logical change: `<KEY> Imperative summary`, single line, no trailers. Umbrella tickets: one commit per listed item.

## Step 5 — Record
Append to $ARGUMENTS:
```markdown
## Implementation
Branches: <repo> `jira/<KEY>-…` (off `<base>` <sha>) · …
Commits: - `<sha>` <message> — <files, what>
Decisions: - <anything you chose that the ticket did not say>
Scripts for the developer to run: - <path> on <env> (<why the agent could not>)
```
Then say what is ready and suggest `/prompts:task-verify $ARGUMENTS`.
