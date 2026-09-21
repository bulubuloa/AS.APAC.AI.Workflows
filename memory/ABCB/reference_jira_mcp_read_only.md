---
name: reference-jira-mcp-read-only
description: "Atlassian MCP write access to Jira (isos site): comments WORK as of 2026-09-21 via mcp__atlassian-isos__addCommentToJiraIssue (ADF with mentions); it was read-only until at least 2026-08-03"
metadata:
  node_type: memory
  type: reference
  originSessionId: 89fd0e2c-d752-4b3e-b33e-c980ddf9c375
  modified: 2026-09-21
---

**Update 2026-09-21:** `mcp__atlassian-isos__addCommentToJiraIssue` on `internationalsos.atlassian.net`
now succeeds — 12 comments posted with `contentFormat: adf`, including `mention` nodes
(Jessie `712020:b27374f5-b2fc-4841-9142-c764cae28063`, Mia DO Huong `712020:d1fa47f6-8aae-43f8-b3f2-3bb18b17635c`;
look others up with `lookupJiraAccountId`). Transitions/assignee not re-tested since.

History: between 2026-07-31 and 2026-08-03 every write failed with
"Access denied: Your organization admin has not authorized the write_jira permission", so comments had
to be written to `issues/` for the user to paste. Try the write first; fall back to the file only if it fails.
