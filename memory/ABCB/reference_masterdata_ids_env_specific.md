---
name: reference-masterdata-ids-env-specific
description: "Aspire masterdatas numeric IDs differ per environment — onboarding SQL must look up by MasterCode, never hardcode"
metadata: 
  node_type: memory
  type: reference
  originSessionId: dad5ab62-3a2f-44e2-8993-ad23e763106c
---

In the Aspire benefit DB, `masterdatas.Id` values are **environment-specific** — the same numeric Id means different things in preprod vs other DBs. A client-onboarding script that hardcodes them will silently point at the wrong row.

Concrete burn (ABE-4838 MSU): the script hardcoded `@periodTypeMasterDataRecurring := 50203` ("confirmed from ABE-4001"), but in the preprod clone `50203 = "Golf"` (SPORTS & RECREATION), not Recurring. The privilege's "Redemption Period" rendered wrong. Correct value was looked up by code: `SELECT Id FROM masterdatas WHERE MasterCode='PERIOD_TYPE_RECURRING'` → 50172 (parent `PRIVILEGE_REDEMPTION_PERIOD_TYPE`); Non-Recurring = `MasterCode='NON_RECURRING'`.

**How to apply:** In onboarding/fix SQL, always resolve masterdata by `MasterCode` (or `MasterNameEN` when MasterCode is NULL — e.g. currency THB is keyed by `MasterNameEN='THB'`, Id 50150, since its MasterCode is NULL), never by literal Id. Validate against a QA-accepted reference client's privileges (e.g. TMI) when unsure of the right value. Two distinct privilege fields: `privileges.PeriodTypeMasterDataId` = the "Redemption Period" (Recurring/Non-Recurring, from masterdatas), and `privilege_redemption_period.RedemptionPeriodTypeId` = the "Type" (e.g. Program Validity=6, from `privilege_redemption_period_type`). Cancellation rule "Cancellable" = `privilege_cancellation_rule_options` Id 5 (not "Cancellable within period of booking"=2).

**Coverage "Support Per Redemption" field (ABF PrivilegePriceListDialog.razor):** for coverage type `FIXED_AMOUNT_PER_REDEMPTION` (masterdatas MasterCode='FIXED_AMOUNT_PER_REDEMPTION', id 50165 in preprod) the UI binds "Support Per Redemption" → `privilege_benefit_coverage.CashBenefit` (NOT `TotalSupportAmount`). So a fixed coverage amount (e.g. 700 THB) must go in `CashBenefit` (+ `CurrencyId`), with `TotalSupportAmount=0`. Putting it in TotalSupportAmount shows as "missing" in the UI. (For `TOTAL_MULTI_REDEMPTION` type it's the reverse: TotalSupportAmount = "Total Support Amount", CashBenefit = "Support Per Redemption" capped ≤ total.)

**Validity end-date display:** storing `...-12-31 23:59:59` renders as +1 day (01/01 next year) because the API serializes UTC and the picker shifts to local (VN +7 etc.). Store end dates at `00:00:00` so the date part survives any TZ offset. See [[reference_dataprocesser_preprod_pipeline]].
