---
name: reference_kpi_s3_upload_triggers_duplicate_job
description: Uploading a file to the KPI S3 prefix itself fires the import rule — queueing the PENDING_INSERT row too soon double-imports it
metadata: 
  node_type: memory
  type: reference
  originSessionId: 6eff9327-ea14-449d-837e-8ecf0043abf5
  modified: 2026-08-05T09:12:01.543Z
---

The EventBridge rule `benefit-import-data-clients-kpi-prod` fires on **S3 object creation** in `production/clients/kpi/`, submitting `ImportDataSourceKPIProd`. So a manual reprocess has TWO job triggers, not one: the upload, plus your own `aws batch submit-job`.

Both jobs read the same latest `customer_import_file_template` PENDING_INSERT row. If the row already exists when the upload-triggered job starts, **both import the file and every record is inserted twice** (KPI has no UUID-collision guard on insert — `ReferenceID` = `PolicyNumber_LicenseNumber` duplicates freely).

**Safe order:** upload to S3 → wait for the auto-triggered job to finish (it no-ops if no PENDING row) → *then* insert the PENDING_INSERT row → then submit. Or skip the manual submit entirely and just let the upload trigger it.

Hit this on 2026-08-05 recovering `SOS_20260317_FIX.txt`/`SOS_20260318_FIX.txt`: file 1 was clean (row inserted 27s after upload, auto-job found nothing), file 2 was uploaded and queued in the same step → 27 duplicate customers, deleted along with 27 `customerprograms` + 135 `privilege_customer_program_validity` rows.

Also note: **filtered recovery files beat full-file re-runs.** Replaying a whole old file overwrites every already-present policy with stale data (all 138 present policies in those two files had been updated since March). Build a file containing only the missing rows — same TIS-620 encoding, CRLF, 4 columns. See [[reference_kpi_reprocess_mechanism]].
