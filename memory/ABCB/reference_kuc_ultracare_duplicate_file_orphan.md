---
name: reference_kuc_ultracare_duplicate_file_orphan
description: "KUC = KPI UltraCare (separate client, 5U- policies); same-day duplicate SFTP files orphan a PENDING_INSERT row that never imports"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7913aa43-39bb-4b75-9338-59f15922bf01
---

**KUC is "KPI UltraCare"** — a SEPARATE client from KPI. ClientCode `KUC`, policies prefixed `5U-...`, SFTP stream `s3://data-processor-sftp/production/clients/kuc/KPI_ULTRA_SOS_YYYYMMDD.txt`, job-def `benefit-kuc-import-prod-job-definitions`, nightly ~02:30 UTC. Pipe-delimited; Thai cols are TIS-620 so **grep needs `-a`** (else matches are silently skipped as "binary"). KUC `customers.ReferenceID` = the bare PolicyNumber (KPI's is `PolicyNumber_plate`).

**Orphan bug (the same applies to KPI):** the import job processes only the **latest** `customer_import_file_template` row `WHERE ClientCode=… AND Status='PENDING_INSERT' ORDER BY CreateOn DESC`. When a client sends **two files for the same day** (e.g. `KPI_ULTRA_SOS_20260609.txt` + `..._20260609-002.txt`, queued ~1s apart), both become PENDING_INSERT, the job runs only the newest, and the **older file is orphaned forever** (every later nightly creates a newer row and picks that). Found 06-09 orphan = 2,041 records, only 310 recovered via later daily files → 1,731 missing incl. the policy a client reported. Reprocess by triggering the job while the orphaned row is the latest PENDING_INSERT (see [[reference_kpi_reprocess_mechanism]]); it flips to INSERT_SUCCESS and upserts. Permanent fix would be to process ALL pending rows, not just the latest. Known still-orphaned: row 1166 `KPI_ULTRA_SOS_20260312.txt` (March).
