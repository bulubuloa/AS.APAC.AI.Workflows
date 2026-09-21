---
description: Fetch a Jira (ABE) ticket and create a task file in issues/
argument-hint: <jira-url-or-key>
---

Fetch the Jira ticket referenced by $1 and create a task file in `issues/`. Fetch only — no code reading, no analysis, no fixes.

## Step 1 — Parse input

`$1` is a key (`ABE-5457`) or a browse URL (`https://internationalsos.atlassian.net/browse/ABE-5457`). Extract the key.

## Step 2 — Fetch via the Atlassian MCP (server `atlassian-isos`, cloudId `internationalsos.atlassian.net`)

1. `getJiraIssue` for the key. Keep: summary, description, status, priority, issue type, labels, components, fixVersions, assignee, reporter, parent, sub-tasks, issue links (direction + link type), created/updated, attachment names.
2. `getJiraIssueRemoteIssueLinks` — Confluence pages and external links.
3. Comments: read all of them; keep author, date, body. Quote them verbatim under Notes — never summarise away a BA decision.
4. For the parent and every directly linked issue, `getJiraIssue` again for summary + status only. One level deep, no recursion.
5. If a remote link points at a Confluence page, `getConfluencePage` it and quote the requirement sections into Context (mark the source).
6. If the MCP is not in the tool list, stop and tell the user to run `/mcp`.

## Step 3 — Write `issues/<KEY>.md`

If the file already exists, ask before overwriting; offer a `-v2` suffix. Preserve the description as Markdown, including tables and checkbox lists. Tag anything you had to infer with `(inferred)`.

```markdown
# <KEY> — <Summary>

> Jira: https://internationalsos.atlassian.net/browse/<KEY>
> Type: <type> · Status: <status> · Priority: <priority> · Fix version: <fixVersions or —>
> Reporter: <name> · Assignee: <name> · Updated: <YYYY-MM-DD>
> Parent: <KEY (status) or —> · Links: <type KEY (status), …>
> Confluence: <page titles or —>

## Context
<description, verbatim Markdown; quoted spec sections if any>

## Goal
<one sentence — what "done" looks like for the BA>

## Requirements
- <3–7 concrete statements, extracted or (inferred)>

## Acceptance criteria
- [ ] <from the ticket, or "- [ ] to be defined during analysis">

## Out of scope
<explicit exclusions, else "not stated">

## Open questions
<ambiguities in the description — feeds the analysis step>

## Notes / comments
- <YYYY-MM-DD> <author>: "<verbatim>"
- Attachments: <names> (download into issues/ — the MCP cannot fetch binaries)

## Analysis
_(appended by /task-analyse)_
```

## Step 4 — Confirm and stop

Print the file path, a one-line summary of the ticket, and the next step:

```
/task-analyse issues/<KEY>.md
```

Do NOT start analysing or coding — the user reviews the file first.
