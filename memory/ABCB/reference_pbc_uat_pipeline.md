---
name: reference-pbc-uat-pipeline
description: "PBC (UOB Concierge, ABE-5223) UAT infrastructure and the two gotchas found standing it up — client_customer_attributes must NOT be merged into PBC validation, and UAT has only a \"Platinum\" tier. Use when working on PBC or onboarding a voucher-code client."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 66f1050d-864d-410b-9652-ec7a47df5c98
  modified: 2026-08-10T14:44:29.422Z
---

## PBC UAT infra (created 2026-08-10, ap-southeast-1)

- SES receipt rule `uat-EMAIL-PBC` in rule set `benefit-receipt-ruleset-sit`:
  `pbc-uat-import@aspirelifestylesasia.com` → `s3://benefit-raw-email-receiving/uat/EMAIL/PBC/`
- Batch job def `benefit-pbc-import-uat-job-definitions` (FARGATE, 1 vCPU / 2 GB, role `AWS-Execution-Role-SIT`)
- EventBridge rule `pbc-uat-email-rule` → queue `benefit-import-uat-job-queue`, job def **revision-pinned**
  (repoint on every new revision), InputTransformer sets `JOBTYPE=CLIENT_PBC_DATA_PROCESSER`,
  `CONNECTION_TARGET=UAT`, `S3_BUCKET_NAME`/`S3_OBJECT_KEY`. PBC reads the raw .eml from those two vars.
- UAT PBC = clients.Id **483**, ~30 000 voucher codes.

Smoke test without touching data: mail a 3-column xlsx with made-up codes — every row comes back
"Invalid voucher code value." and nothing is written. Creating the SES rule also drops an
`AMAZON_SES_SETUP_NOTIFICATION` object in the prefix, which fires one job that correctly reports
"No files to process."

## Gotchas

1. **Do not merge `client_customer_attributes` into PBC row validation.** PBC rows are voucher codes,
   not customer profiles; the client's attribute config has a numeric `Status` field, so every row
   failed "Status is invalid — not a valid number". PBC validates against its own three template
   columns only ([[feedback-dataprocesser-fieldmapping]] does not apply to this client).
2. **Tier names may be multilingual JSON** (`{"en":"Platinum"}`) — accept every locale value plus the
   raw string. UAT has exactly one tier configured, **Platinum**; a file saying "Gold" is correctly
   rejected with "Invalid customer tier.", so use Platinum in test files.
