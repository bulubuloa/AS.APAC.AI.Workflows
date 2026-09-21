---
name: reference-sor-sompo-pipeline
description: "SOR (Sompo) deploy pipeline — ECR repos, job defs, scheduler resolves job def by NAME, and the UAT CONNECTION_TARGET gap"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 89fd0e2c-d752-4b3e-b33e-c980ddf9c375
  modified: 2026-08-03T17:34:44.376Z
---

SOR (Sompo) does NOT follow the `{client}-preprod-email-rule` pattern in
[[reference-dataprocesser-preprod-pipeline]]. Verified 2026-07-30/08-04:

- **Prod**: job def `sompo-import-data-client-prod-job-definition`, queue
  `sompo-client-import-data-queue-prod`, image = shared
  `apac-benefit-data-processer-production` (was `:v1.5`).
- **Prod trigger = EventBridge *Scheduler*** (not an Events rule):
  `benefit-data-batchjob-insert-file-sompo-client-time-1330-prod` and `...-2130-prod`.
  Their Input references the job definition **by name**, so Batch resolves the latest
  ACTIVE revision — registering a new revision is enough, no target repoint.
  Reverting therefore means deregistering the newer revisions.
- **UAT**: job def `sompo-import-data-client-uat-job-definition`, queue
  `sompo-client-import-data-queue-uat`, image = **`aspire-common-job-uat:latest`**
  (a different repo from every other client; only SOR uses it, so pushing `:latest`
  affects SOR alone). UAT schedule is DISABLED — submit the job manually.
- **UAT job def has no `CONNECTION_TARGET`**, and the code reads that (not `ENV`), so it
  defaults to `LOCAL` and tries 127.0.0.1:3375. Always pass
  `CONNECTION_TARGET=UAT` in containerOverrides, or the job dies on MySQL connect.
- Prod image tags are **per client** (`tpi-v1.5`, `fwd-1.9`, `tri-20260706-1`); the bare
  `v1.0`–`v1.6` tags already exist and are referenced by other job defs — never reuse one.
- SOR input/output S3 all live under one prefix: `BUKET_FOLDER_GET_FILE`
  (`production/clients/sompo/`, UAT `staging/clients/sompo/`), with
  `FileProcessed/` and `FileTransferToClientService/` beneath it.
