---
description: Analyse a task file — root cause / design, verified facts, blast radius, questions, plan. Read-only.
argument-hint: <path-to-task-file>
---

Analyse the task described in $ARGUMENTS and append an `## Analysis` section to it. This step is **read-only**: do not edit code, do not run any SQL other than SELECT, do not transition or comment on the ticket. Output is text in the task file.

## Rules

- Cite every code claim as `file:line`. Cite every data claim with the query and its row count. Tag every number `[measured]` (query is in the file, re-runnable) or `[assumption]`.
- Anything surprising needs two sources (code + data, or code + log) before it is stated as fact.
- Use an Explore sub-agent for broad sweeps ("every reader of column X across the solution"); keep judgement in the main session.
- UAT first. Query prod only when UAT cannot answer, SELECT-only, aggregates over row dumps, no customer PII in the conversation.
- Business rules are questions for the BA/QA, not decisions for you.
- Time-box: if the sweep keeps widening, narrow to the repo/controller/table named in the ticket and say what you left out.

## Step 1 — Load the brief

Read $ARGUMENTS and every Confluence page it links. Restate the goal in one sentence and list what you will need to verify.

## Step 2 — Locate the code

Find every touchpoint across the repos in this workspace (ABMB RoadSide `BkkIsos47.sln`, ABVB VendorServerless, ABF, ABCB): controllers, EF/SQL queries, stored procedures, views, front-end calls, sync jobs, schedulers, reports. Produce a touchpoint table with `file:line`.

## Step 3 — Hypotheses

Write 2–3 candidate causes (or design options for a feature), ranked, each with the evidence that would confirm or kill it.

## Step 4 — Verify against data and logs

Run read-only queries through the existing tunnels (`sqlcmd` / `mysql`), call the Kontent Delivery API for the environment in question, and search CloudWatch Logs (`aws logs filter-log-events` / Logs Insights) for exceptions. Record every query and count.

## Step 5 — Root cause / design

State the cause with the exact code path and explain why the ticket's symptom follows from it. For a feature, state the design that fits existing patterns and the smallest backward-compatible sequence of changes.

## Step 6 — Blast radius

How many rows / users / clients share the condition? Which other flows read the same field? What breaks under the obvious fix? Rate each touchpoint 🔴 breaks / 🟠 degrades / 🟢 unaffected.

## Step 7 — Open questions

List every choice that is a business rule as a question with the options and the consequence of each. Use `AskUserQuestion` if the answer blocks the plan; otherwise leave them for the Jira comment.

## Step 8 — Plan

Numbered: repo + files to change, order, DB scripts, config/Parameter Store, tests, Playwright verification steps, release-note line, rollback.

## Step 9 — Write

Append to $ARGUMENTS:

```markdown
## Analysis
Verified <date> against <env> (<DB>, read-only) and <CMS env>. Code = <branch> (<sha>).

### Understanding
### Root cause / design
### Facts
| Fact | Value | Source / query | Tag |
### Blast radius
| # | Feature | Code | Reads | Impact if changed | Sev |
### Open questions for BA/QA
### Plan
```

Then tell the user it is ready for review and offer to post a condensed version as a Jira comment (`addCommentToJiraIssue`) — only after they say yes.
