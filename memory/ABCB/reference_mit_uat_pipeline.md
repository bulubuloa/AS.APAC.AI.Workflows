---
name: reference_mit_uat_pipeline
description: "MIT (Mitsubishi) UAT data-processor pipeline created 2026-09-08 for ABE-5157 — job def, SES rule, EventBridge rule, test-drop entry"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 86277fe9-ddf1-46c1-8f4e-68cd2852bde6
  modified: 2026-09-08T03:28:29.912Z
---

MIT had no UAT environment until 2026-09-08 (only preprod + prod). Created for ABE-5157:

- SES receipt rule `uat-EMAIL-MIT` in rule set `benefit-receipt-ruleset-sit` → `mit-uat-import@aspirelifestylesasia.com` lands in `s3://benefit-raw-email-receiving/uat/EMAIL/MIT/`
- EventBridge rule `mit-uat-email-rule` (prefix `uat/EMAIL/MIT/`) → queue `benefit-import-uat-job-queue`, job def **pinned by revision ARN** `benefit-mit-import-uat-job-definitions:1` — a new revision needs the target repointed (same trap as [[reference_dataprocesser_preprod_pipeline]])
- Job def image comes from `apac-benefit-data-processer-pre-production` with an immutable per-release tag (all UAT email clients share that repo; SOR/AOI do not — see below)
- MIT added to the QA test-drop tool as an `email` kind, folder `uat/EMAIL/MIT` ([[reference_dataprocessor_testdrop_tool]])

AOI's UAT job def `aoi-import-data-client-uat-job-definition` uses its **own** ECR repo `aoi-client-uat-import-data:latest`, so pushing `:latest` deploys AOI with no job-def revision needed. Its EventBridge rule `aoi-client-import-data-uat-rule` is DISABLED — QA triggers AOI through the test-drop tool.

UAT program numbers (env-specific, see [[reference_masterdata_ids_env_specific]]): AOI `AIOI00001` → program 672 / tier 2171; MIT `285MIT824842` → program 594 / tier 1779 (its ProgramCode `MIT-CODE-01` deliberately diverges).
