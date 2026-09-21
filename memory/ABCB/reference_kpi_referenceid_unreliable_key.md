---
name: reference_kpi_referenceid_unreliable_key
description: "Never reconcile KPI customers on ReferenceID — it is NULL or the person's name for some rows; use CustomerAttributes.PolicyNumber"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 6eff9327-ea14-449d-837e-8ecf0043abf5
  modified: 2026-08-05T10:02:04.937Z
---

`customers.ReferenceID` for KPI is *usually* `PolicyNumber_LicenseNumber` (e.g. `25-26-00031885_4ขค2569 กรุงเทพมหานคร`), older rows are the bare policy — **but a minority are NULL or hold the customer's NAME** (`Suwanna Jeenasud`, `บุญล้อม ยิ้มเพลิน`). Reconciling source files against `ReferenceID` therefore reports phantom missing records.

**Always key on `json_unquote(json_extract(CustomerAttributes,'$.PolicyNumber'))`** — it is populated on all 409k KPI rows. One scan pulling `Id, ReferenceID, CreatedOn, PolicyNumber` for the whole client takes ~1 min through the tunnel and is far faster than N `CustomerAttributes LIKE '%policy%'` queries (those are minutes *each* over 409k rows — don't).

Cost of getting this wrong (2026-08-05): a ReferenceID-keyed reconciliation of all pre-2026-03-19 KPI files reported **123 missing**; the PolicyNumber-keyed one showed the true figure was **64** — 45 of the difference existed with NULL/name ReferenceIDs and 14 were long-plate rows likewise mis-keyed. Only those 64 (the 21-char-plate rejects in `SOS_20260317/18`) were ever really missing. See [[reference_kpi_reprocess_mechanism]] and [[reference_kpi_s3_upload_triggers_duplicate_job]].
