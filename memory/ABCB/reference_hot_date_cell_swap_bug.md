---
name: reference_hot_date_cell_swap_bug
description: HOT (Honda) date cells rejected ~75% + swapped day/month; fixed with CommonDate.TryParseDateCell (same class as FWD bug)
metadata: 
  node_type: memory
  type: reference
  originSessionId: a694c266-59a5-4182-810c-9e1f2b621f47
---

ABE-4983: HOT Data Processor marked ~75% of records invalid. Root cause was NOT bad data — Excel Delivery/End dates are real DateTime cells. The old reader (`HOTProcesserFile.ReadHondaCustomersFromXlsx`) stored them via `rowValues[i].ToString()`, which the prod AWS Batch container (InvariantCulture) renders month-first "MM/dd/yyyy". `HondaConstanst.ValidateByFieldConfigsHonda` then validates EffectiveDate/ExpirationDate with dd/MM-only formats → any row with day-of-month > 12 rejected (~75%), and the survivors (day ≤ 12) got day/month **silently swapped** (e.g. 1-Apr stored as 4-Jan). On the 2 Jul prod file (37,206 rows) OLD = 671 correct / 9,000 swapped / 27,535 rejected.

Fix: read date cells with `CommonDate.TryParseDateCell(cell).Raw` (returns typed DateTime formatted dd/MM/yyyy, no culture round-trip) → 100% correct on both real files. This is the SAME bug class already fixed for FWD (documented at `CommonDate.cs:45-56`, "FWD all-rows-invalid bug"). When onboarding/reviewing any client that reads Excel date cells, use `TryParseDateCell`, never `cell.ToString()`.

Only mandatory HOT field is `ChassisNumber` (client_customer_field_config ClientID 38) — blank Plate/CarColor are red herrings. Prod DB reachable via local tunnel `127.0.0.1:3382` (creds = `connectionStringBenefitProduction` in secret `benefit-connection-string-preprod`, table names lowercase). Local test: `HOTLocalTest.RunValidationTest()` / `RunDateAccuracyTest()`. Related: [[reference_dataprocesser_preprod_pipeline]], [[feedback_dataprocesser_fieldmapping]].
