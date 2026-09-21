---
description: Verify an implemented task with evidence — browser, database, logs — against its acceptance criteria. Read-only on shared environments.
argument-hint: <path-to-task-file>
---

Produce evidence for every acceptance criterion in $ARGUMENTS and write it under `## Verification`. "It builds" is not evidence.

## Rules
- Read-only on SIT/UAT/PROD databases (SELECT). Never apply a script or an UPDATE to make a check pass; list it for the developer instead.
- Prefer the real thing: the deployed SIT/UAT app in a browser (Playwright MCP), the real report/API, the real DB counts. When the change is not deployed yet, verify what can be verified without it (run the new SQL body as a plain SELECT with parameters substituted; call the current API to record the *before* state; unit tests) and say so.
- Use the shared UAT/SIT test account, never a personal prod account. Screenshots go to `issues/<KEY>-<step>.png`; they may hold test-customer data — never into a repo or a PR.
- Cap at ~5 fix–rebuild–recheck cycles per issue; then report the latest state and the diagnosis.

## Step 1 — Map criteria to checks
For each `- [ ]` acceptance criterion in $ARGUMENTS decide the check: browser path (page, action, expected), DB query (before/after), API call, log search (`aws logs filter-log-events`), unit test.

## Step 2 — Run the checks
Browser: navigate, act, `browser_snapshot`/`browser_take_screenshot`, read network requests when the UI hides an error. DB: the queries from the Analysis, re-run, counts side by side. Logs: the minute of the test, no new exceptions.

## Step 3 — Write the evidence
Append to $ARGUMENTS:
```markdown
## Verification
| Check | How | Result | Evidence |
|---|---|---|---|
| <criterion> | <page/query/command> | <pass/fail + numbers> | <screenshot path / query in file> |
Not verified: - <what> — <why> — <what the developer must do first (deploy X, run script Y)>
```
Tick the acceptance criteria that passed (`- [x]`). Fix real defects you found (back to code, new commit, re-verify) and add them to the table. Then suggest `/prompts:task-deliver $ARGUMENTS`.
