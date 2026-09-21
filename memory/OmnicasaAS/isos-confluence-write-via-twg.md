---
name: isos-confluence-write-via-twg
description: "ISOS Confluence writes are blocked on the Atlassian MCP; use the twg CLI. AD space id, AI folder + doc-series page ids."
metadata: 
  node_type: memory
  type: project
  originSessionId: a65b07ca-5f93-4bd0-afcb-628fb78d06bd
  modified: 2026-09-21T02:33:17.514Z
---

On internationalsos.atlassian.net the Atlassian MCP (`atlassian-isos`) is read-only for Confluence — `createConfluencePage` fails with "organization admin has not authorized the write_confluence permission". It also cannot see Confluence *folders* (404 / CQL ancestor returns 0).

**Why:** org-level MCP scope restriction; the `twg` CLI (`~/.local/bin/twg`, v1.3.1, OAuth as hoangq) has full write and folder support.

**How to apply:** publish with
`twg confluence content create --space-id 64782337 --parent-id <id> --content-type page --title "…" --body-file x.html --format html --ack-body-formats -y -o json`
(same HTML+data-type format as the MCP guide). `twg confluence tree <id>` shows hierarchy; `twg confluence content get <id> -o json` gives the snapshotToken for updates.

IDs — AD space `64782337`; AI sharing folder `6837207196`; "AI in the Development Workflow" series (created 2026-09-21): overview `6837665931` → 1. MCP Connect `6837305456`, 2. Task Fetch `6837567589`, 3. Task Analysis `6838190087`, 4. Implement & Verify `6837698635`, 5. Review & Release `6837895231`, Worked example Sprint 70 `6837895252` (both phases documented; PR link still to be added once confirmed), Worked example ABE-5461 `6837207394` (branches `jira/ABE-5461-payment-report-jobid` in ABCB.Clone + ABF, not pushed; SP not applied on UAT). Snapshot token for update is just `v:<version>`. Jira comments via the MCP (`addCommentToJiraIssue`) WORK as of 2026-09-21 (12 posted in the ABCB session) — only Confluence writes are blocked. Sentry is NOT used on RSA/Benefit (CloudWatch Logs is) — keep it out of ISOS docs. Project commands `/task-fetch` (Jira) + `/task-analyse` live in `OmnicasaAS/.claude/commands/`. Source HTML was in the session scratchpad only — re-read pages before editing.

Data Processors folder `6837698656` → overview `6837534805` + 25 client pages (ids in `Omnicasa.Mobile.ABCB/docs/data-processor/confluence/page_ids.json`; generator `gen.py` + facts `clients.py` there — edit facts, regenerate, `twg … update`).

**Diagrams:** Mermaid Chart / draw.io / PlantUML macros written via API render EMPTY (apps only render macros made in their editor). Working recipe: render Mermaid → PNG (mrender.html in Playwright), upload as page attachment with the Confluence REST API (basic auth `hoang.quach@aspirelifestyles.com` + API token in `~/.config/atlassian/token`, header `X-Atlassian-Token: nocheck`), embed `<figure data-type="media-single"><div data-type="media" data-id=<fileId> data-collection=contentId-<pageId>>`; keep the Mermaid source in a `<details>` expand. Media ids in ABCB `docs/data-processor/confluence/media_ids.json`.

Part 0 (setup kit) page `6838812674`. The kit itself: `OmnicasaAS/ai-workspace` (git; memory dirs for OmnicasaAS/ABCB/ABMB are symlinks into `ai-workspace/memory/`, task files in `ai-workspace/issues/`). At the end of a ticket: commit the memory + issues changes there.
