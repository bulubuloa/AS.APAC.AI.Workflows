---
name: reference-msc-msig-concierge
description: "MSC (MSIG Concierge, ABE-5249) data processor — UAT and PROD ids/infra, the ProgramNumber 888888 finding, and the missing SFTP-to-processor bridge in production. Use when releasing MSC or debugging its imports."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 66f1050d-864d-410b-9652-ec7a47df5c98
  modified: 2026-08-14T15:18:24.565Z
---

## MSC = MSIG Concierge (ABE-5249), daily CSV over SFTP

**ProgramNumber `888888` turned out to be the same in both environments** (verified 2026-08-13). The
constant was written assuming it was UAT-only; in fact prod program **296** also carries ProgramNumber
`888888`, so no code change was needed for the prod release. Still resolve by ProgramNumber, never by id.
Symptom when wrong: customers import fine but get no program, log says `no program found for ProgramNumber ...`.

## Environment ids (verified 2026-08-13)

- UAT: client **545**, program **896**, tier **2964** `{"en":"MSC"}`
- PROD: program **296**, ProgramNumber `888888`
- 13 `client_customer_field_config` rows; `PolicyNumber` is the UUID with **MaxLength 15**, and all 11
  file-mapped fields are mandatory — a long policy number or one blank cell rejects the row. Both are
  config, not code; check against MSIG's real file before blaming the processor.
- `InforceAsAt` is configured TEXT (not DATE), so no date validation applies to it.

## One policy legitimately maps to many customers

MSIG group policies list one row per traveller (`RISK_NO` distinguishes them). The upsert keys on
policy + ID card, so e.g. policy 43236983 correctly yields 10 customers with distinct names/ID cards.
A `GROUP BY PolicyNumber HAVING COUNT(*)>1` check therefore looks alarming but is normal — compare
names and IDCard before calling it a duplicate.

## Pipeline (differs from the email clients)

SFTP drop → **something must** write the file to `s3://data-processor-sftp/{env}/clients/msc/` **and**
insert a `customer_import_file_template` row (`PENDING_INSERT`) → S3 event → EventBridge → Batch.
The job finds its work from that DB row, not from the event, and takes the **oldest** pending row.

**The bridge was missing until 2026-08-14** — the prod pull-file lambda
(`common-benefit-lambda-pullfile-sftp-production`) has hardcoded Chubb/CardX/SCB handlers and no MSC one,
so every daily file stranded. UAT never caught it because QA drops straight into `uat/clients/msc/`,
which is already the folder the rule watches.

Now bridged by lambda **`msc-sftp-bridge-production`** + EventBridge rule **`msc-msig-sftp-upload-rule`**
(bucket `sftp-aspirelifestylesasia-com`, prefix `msig/msig_prod/`). It inserts the pending row then copies
to `production/clients/msc/`; source and runbook live in `DataProcesser/infra/msc-sftp-bridge/`.
**If MSC is ever added to the pull-file lambda, delete this lambda and rule or files get queued twice.**
An EventBridge rule was used rather than a bucket notification so it cannot disturb the ANZ lambda
notifications already on that bucket. To test the trigger without polluting the prod client report, drop
a `.txt` — the rule fires and the lambda skips on the extension guard.

Prod infra that does exist: job def `benefit-msc-import-prod-job-definitions` and rule `msc-prod-sftp-rule`
on prefix `production/clients/msc/`. Both rules reference the job def **by name**, so a new revision
deploys without repointing. `LIST_EMAIL_TO` on the prod job def is still only hoang.quach@ — real
recipients were never set. See [[reference-dataprocesser-uat-pipeline]] and [[reference-handback-run-races]].

## Known queue defects (unfixed)

- The pending-row claim is **not atomic** — two jobs can pick the same row and import a file twice
  (observed in both UAT and prod).
- One row per run: extra pending rows just sit there until another event fires.
- On the failure path the EF context is poisoned, so the status update fails and the row stays
  `PENDING_INSERT` — which then feeds the double-import above.
