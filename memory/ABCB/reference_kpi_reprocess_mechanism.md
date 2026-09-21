---
name: reference-kpi-reprocess-mechanism
description: "How to re-run a KPI (SOS_*.txt) prod file import, and the License-length rejection incident"
metadata: 
  node_type: memory
  type: reference
  originSessionId: dad5ab62-3a2f-44e2-8993-ad23e763106c
---

KPI ingests daily `SOS_YYYYMMDD.txt` from `s3://data-processor-sftp/production/clients/kpi/`. The Batch job does NOT take the file from the S3/EventBridge event — it reads the **latest** row `WHERE ClientCode='KPI' AND Status='PENDING_INSERT' ORDER BY CreateOn DESC` from table **`customer_import_file_template`** (cols: Id, FileName, Status, CreateOn, ClientCode, MessageImport, IsArchive). So to **re-run a specific file**: INSERT a `PENDING_INSERT` row for that FileName (CreateOn=now) → submit Batch job to queue `benefit-import-prod-job-queue`, job def `benefit-kpi-import-prod-job-definitions` (carries all env). The job processes it and flips the row to `INSERT_SUCCESS`. **Only ever one PENDING_INSERT row at a time** — a stale one hijacks the nightly ~01:00 UTC run. Files are incremental (rejected rows are NOT re-sent later), so each affected file must be reprocessed individually. Override `RECIPIENT_EMAIL`/`CC_EMAIL_ADDRESSES` on the manual submit to avoid emailing the client. KPI UUID key = PolicyNumber.

Incident (May 2026): `LicenseNumber` field config MaxLength=20 rejected Thai plates with a leading digit + `กรุงเทพมหานคร` (21 chars) → "License Number has invalid TEXT value" → ~44 daily files (SOS_20260324→SOS_20260513) lost 7–54 records each; customers missing from Benefit. Fix = widen MaxLength (now NULL/255 in prod `client_customer_field_config`); reprocess affected files. Full runbook: `issues/KPI-license-length-reprocess-runbook.md`. Prod DB reachable via bridge 127.0.0.1:3382 (preprod bridge = 3377). See [[reference_masterdata_ids_env_specific]].
