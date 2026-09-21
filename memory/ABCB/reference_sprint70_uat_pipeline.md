---
name: reference_sprint70_uat_pipeline
description: "UAT deployment for the 12 sprint-70 clients (TRI TTR MSU TMI MAZ AEO CHU KTC MSH KUC SMC KPI) — job defs only, no SES/EventBridge rules; the test-drop tool submits the job with S3 overrides; PGP UAT keys for KTC/SMC; KPI empty-DB safety stop"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 84a3942d-ec01-44a6-8e79-5d611c64bb41
  modified: 2026-09-21T03:13:08.089Z
---

Built 2026-09-21 for epic ABE-5148 (see [[reference_program_number_mapping_sprint70]]).

- Image: `apac-benefit-data-processer-pre-production:uat-sprint70-20260921-NN` (buildx linux/amd64 from `DataProcesser/`).
- Job defs `benefit-{tri,ttr,msu,tmi,maz,aeo,chu,ktc,msh,kuc,smc,kpi}-import-uat-job-definitions` (cloned shape of the CSM UAT def: role `AWS-Execution-Role-SIT`, `CONNECTION_TARGET=UAT`, RECIPIENT_EMAIL JSON array). Registration script pattern lives in the session scratchpad `jobdefs.py`; deploy = register a new revision (test-drop resolves by NAME, so no repoint).
- **No SES rule and no EventBridge rule** for any of the 11 — the QA test-drop tool (`DataProcesser/infra/dataprocessor-testdrop/lambda_function.py`) is the only UAT trigger. It drops the file/MIME and submits the job with `S3_BUCKET_NAME`/`S3_OBJECT_KEY` overrides (what the prod InputTransformer injects). Email-kind clients get their MIME under `uat/EMAIL/{TRI,TTR,MSU,MSIGHome}/`.
- Drop locations: TMI `sftp-aspirelifestylesasia-com/tokiomarine/tokiomarine_uat/` (NOT `_development` — that prefix fires the preprod rule); AEO/CHU/KTC/SMC `aspire-internal-app/uat/clients/{aeon,chubb,ktc,scb-card-x}/`; KPI/KUC `data-processor-sftp/uat/clients/{kpi,kuc}/` + `customer_import_file_template` row (SMC's row uses ClientCode `SMC_CARDX`, FileName ends `.pgp`).
- PGP: KTC decrypts with `Benefit-DataProcesser-Client-KTC-UAT-Key-Decrypt` (hardcoded, also in prod!); SMC decrypts with `SMC_DECRYPT_SECRET` (UAT job def → `Benefit-DataProcesser-Client-SMC-UAT-Key-Decrypt`, passphrase hardcoded `Aspire1505`). The tool encrypts with `...-KTC-UAT-Key-Public` / `...-SMC-UAT-Key-Public` (pgpy 0.6.0 vendored; 0.5.4 breaks on current cryptography). TMI's `ASPIRE_RSA*.csv` feed has no UAT/PROD key secret at all — only the Thai Orix / Mitsubishi xlsx templates are testable.
- Lambda role `benefit-dp-testdrop-uat-role` policy `dp-testdrop-uat` must list each new prefix + job def + the two public-key secrets (IAM writes, secret writes and UAT config UPDATEs are blocked in auto mode — hand the user a script).
- Gotchas found by the real runs: KPI aborts silently when the client has 0 customers in the DB (UAT KPI is empty) — now publishes a Failed report; UAT AEO field config had `EmailAddress` mandatory + names as UUID (prod: `ReferenceID` mandatory UUID) so every AEO row was invalid; UAT tier names are `{"en": ...}` JSON so exact-string tier matches (old TMI) find nothing; MSH reader needs 10 columns (cols 8+9 concatenate into AddressEN).
- Verified working on UAT (2026-09-21, image -04, job def rev 4): TRI, TTR, MSU, TMI (Thai Orix), AEO, CHU, KTC, MSH, KUC, SMC, MAZ (768/2686) — reports in `aspire-dataprocessor-handback-report/{code}/UAT/`, programs/tiers attached by ProgramNumber (KTC card types I/S → 364/1390 & 368/1394; SMC X/B → 116/1003 & 121/1008). KPI verified after seeding 50 prod customers into UAT via `kpi_onboard.py` (prod→UAT copy is PII-blocked in auto mode; user runs it; `~/s70` symlinks the scratchpad). KPI never reports SameData — its update condition is date-based and always true, so unchanged rows count as Updated (pre-existing). UAT KPI `LicenseNumber` MaxLength is still 20 (prod widened to NULL after the 2026-05 incident), so 21-char Thai plates are Invalid on UAT only.
- `CommonDate.ConvertExpireDate("13/99")` used to throw and abort the whole KTC file — fixed 2026-09-21 (returns null → row invalid).
