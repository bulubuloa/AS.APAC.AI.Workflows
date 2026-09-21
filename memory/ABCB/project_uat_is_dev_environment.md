---
name: project-uat-is-dev-environment
description: "As of 2026-07-27 DataProcesser development and testing happens on UAT/staging, not preprod — the preprod Aurora cluster is stopped."
metadata: 
  node_type: memory
  type: project
  originSessionId: 80283ccc-74cb-4f61-bc9d-6c4a0ce386f0
  modified: 2026-07-27T02:55:21.065Z
---

Develop and test DataProcesser on **UAT (staging)**, not preprod. The preprod Aurora cluster
`preprod-20270707` is stopped, so any preprod Batch job fails with
"Unable to connect to any of the specified MySQL hosts" regardless of the image.

**Why:** user instruction on 2026-07-27 after two preprod smoke tests failed on the stopped DB.

**How to apply:** deploy and smoke-test against the UAT stack — `{client}-uat-email-rule`,
`benefit-{client}-import-uat-job-definitions`, queue `benefit-import-uat-job-queue`,
S3 prefix `uat/EMAIL/{Client}DataProcessor/`, `CONNECTION_TARGET=UAT`. Same bump procedure as
[[reference-dataprocesser-preprod-pipeline]] (register new job def revision, repoint the rule —
targets pin a revision ARN). Take recipient emails from the rule's existing InputTransformer;
never substitute a personal address.
