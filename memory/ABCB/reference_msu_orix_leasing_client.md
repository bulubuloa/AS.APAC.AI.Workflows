---
name: reference_msu_orix_leasing_client
description: "\"Roadside ORIX\" data = MSU client (Mitsui Sumitomo Insurance, ms-ins.co.th), NOT TMI/Tokio Marine Thai Orix Group — easy to confuse"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7913aa43-39bb-4b75-9338-59f15922bf01
---

**"Member Data Roadside ORIX for Aspire (Thailand)" belongs to the MSU client, not TMI.** ORIX appears in TWO unrelated places — don't confuse them:
- **MSU** = Mitsui Sumitomo Insurance (sender domain `ms-ins.co.th`). File = encrypted xlsx `…Aspire_Thai ORIX Leasing (VMI)Report.xlsx`, sheet `DATA`, 17 cols. Policy Number format **`BKD/XXX /25-NNNNNN`** with an embedded space (e.g. `BKD/VEV /25-017884`, `BKD/VHC /25-002040`). ClientID 98, ClientCode `MSU`.
- **TMI** = Tokio Marine, has a separate "Thai Orix Group" tier whose policies are chassis-style (`DW7069SE2826`). Unrelated to the MSU ORIX file.

**MSU specifics:**
- Prod email inbox: `s3://benefit-raw-email-receiving/prod/EMAIL/MSU/`; EventBridge rule `msu-prod-email-rule`; import address `msu-prod-import@aspirelifestylesasia.com`; job-def `benefit-msu-import-prod-job-definitions`. Pipeline went live ~2026-06-02.
- xlsx is password-encrypted (CDFV2/OLE). Password env `MSU_EXCEL_PASSWORD`, default **`Aspire@123`** (no prod override). Decrypt with `msoffcrypto` + that password.
- **customers.ReferenceID is NULL for MSU** — the PolicyNumber lives in `CustomerAttributes` JSON (`"PolicyNumber": "BKD/VEV /25-017884"`). To check presence: `WHERE ClientCode='MSU' AND REPLACE(CustomerAttributes,' ','') LIKE '%BKD/VEV/25-017884%'`. Embedded space is PRESERVED (only Trim, no collapse).
- **`LicenseNumber` (Excel "Register number") IsMandatory=1** in prod `client_customer_field_config` (join on ClientID, table has no ClientCode col). Rows with a BLANK plate are rejected as invalid → never imported. In the 02-Jun file, **472 / 4742 rows had blank Register number** (≈ the gap vs 4,273 imported). This is why brand-new/unplated leasing vehicles silently go missing. PolicyStatus has NO allowlist — `RENEW`/`NEW` both import fine.

See [[reference_customer_name_two_places]] for the core-column-vs-JSON split, and [[reference_handback_failure_reason_field]] for handback reason reporting.
