---
description: Hand a verified task over — PR text, QA comment on the ticket, release notes, the list of human steps, memory notes.
argument-hint: <path-to-task-file>
---

Turn $ARGUMENTS into the hand-off artefacts. Nothing here pushes, merges, transitions or deploys; the developer does those with what you prepare.

## Step 1 — Rebase check
For each branch: `git fetch origin <base>`; if behind, rebase and rebuild; report the result.

## Step 2 — PR description (one per repo), written to `issues/<KEY>-pr-<repo>.md` and shown
```markdown
<KEY> <Imperative summary>

## Summary
- …
## Decisions (please review)
- … (omit if none)
## Test plan
- [x] <criterion> — <how verified, evidence>
- [ ] <not verified> — <why, what must happen first>
## Deploy notes
- target branch `<base>` (<env>); scripts to run before deploy; ship-together dependencies on other repos
```
Target branch = the base branch from `## Implementation`. Give the developer the push commands and the "create pull request" links (Bitbucket: `…/pull-requests/new?source=<branch>&dest=<base>`).

## Step 3 — Jira comment for QA
Draft: what is ready and where (env, branch, build), how to test (steps, test data, the tool), what to verify, developer evidence (counts, screenshots attached by the developer), open questions for BA. Mention QA with `lookupJiraAccountId` → real account ids. Show the draft; post with `addCommentToJiraIssue` **only after the developer says yes**. Do not transition the ticket.

## Step 4 — Release
Append to $ARGUMENTS:
```markdown
## Release
Flow: `jira/<KEY>-…` → `<base>` (<env>, QA) → <next branches>. Scripts: <path> on each DB ahead of the deploy. Release-note line: "<KEY> <one sentence for the BA>". Rollback: <revert commits / previous SP script>.
Human steps: 1. push … 2. PR … 3. run script … 4. QA … 5. BA answers …
```
If the ticket is part of a release train, add the same lines to the train's release page draft.

## Step 5 — Memory
Write the non-obvious things this ticket taught (environment facts, drift, gotchas, who decides what) as memory notes in `ai-workspace/memory/<project>/` (one fact per file, front-matter, pointer line in `MEMORY.md`). Tell the developer to commit `ai-workspace/`.
