---
name: reference_confluence_dataprocessor_pages
description: "Confluence docs for every DataProcesser client live under AD folder 6837698656 (overview 6837534805, one page per client); generator + facts in docs/data-processor/confluence/ — read them first, update them after a change"
metadata:
  node_type: memory
  type: reference
---

Every DataProcesser client (25: AEO AOI CHU CSM FWD HOG HOT KPI KTC KUC KXA MAZ MBZ MIT MSC MSH MSU PBC SMC SOR TMI TPI TRI TTR TYT) has a Confluence page under **AD → folder "APAC Aspire Benefit Data Processors" (6837698656)**, parent page **6837534805** "Benefit Data Processors — Architecture, Clients, Deploy & Test" (created 2026-09-21). Page ids in `docs/data-processor/confluence/page_ids.json`.

Each client page: identity/JOBTYPE/files, pipeline per env (SES rule, S3 landing, EventBridge rule + state, queue, job def + revision + by-name/revision-pinned, image, CONNECTION_TARGET), input format/reader/password/UUID/FieldMapping, program mapping, deploy specifics, how to test + manual submit template, gotchas, open items. The overview holds the architecture, env table, shared code, client matrix, ingestion patterns, deploy procedure, testing tools, onboarding checklist, cross-cutting gotchas.

**How to apply:** before touching a client, `twg confluence content get <id>` its page (or read `docs/data-processor/confluence/clients.py`, the same facts). After a deploy/change, edit `clients.py`, run `gen.py`, republish with `twg confluence content update <id> --snapshot-token "v:N" --body-file pages/<CODE>.html --format html --ack-body-formats -y`. The Atlassian MCP cannot write on this tenant; twg can. See [[reference_dataprocesser_preprod_pipeline]], [[reference_program_number_mapping_sprint70]].
