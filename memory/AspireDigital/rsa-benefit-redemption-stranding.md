---
name: rsa-benefit-redemption-stranding
description: "RSA Accept fails with Benefit's EF error — the redeemed-roadside 504 stranding bug, its manual unblock, and which repo still needs the fix"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4793d1c2-bae2-42da-a13c-8cd5820891c1
  modified: 2026-08-31T06:18:51.033Z
---

**2026-08-31 prod incident.** Clicking Accept on an RSA job failed with *"An error occurred while saving the entity changes"* — which is **Benefit's** EF error relayed verbatim, not RSA's. Tell them apart by exception type: RSA's own EF failure is `DbUpdateException`; a relayed one is `ApplicationException` (RSA rethrows `res.Messages[0]` at the `throw new ApplicationException($"{res.Messages[0]}")` sites in `MswsController`). This cost hours of looking in the wrong system.

**Mechanism:** `customer_redeemed_privileges.RoadSideJobId` is UNIQUE on the Benefit MySQL (`Aspire`). On job 26JB063257, the first Accept got a **504** from `POST /api/clients/privileges/redeemed-roadside` — Benefit *did* create the row (id 308720, 3 seconds after the 504) but RSA never received the id, so `cloud.JobInfo.cusRedeemedPrivilegeIdBenefit` stayed NULL. Every retry then re-inserted the same `RoadSideJobId` → duplicate key → Benefit's EF throws → relayed to the operator. Retrying can never succeed.

**Manual unblock** (worked, ran 2026-08-31 13:15): find the row on Benefit (`SELECT Id FROM customer_redeemed_privileges WHERE RoadSideJobId='<jobId>'`), then `UPDATE cloud.JobInfo SET cusRedeemedPrivilegeIdBenefit=<Id> WHERE jobId='<jobId>'`. Accept then skips the redemption call entirely — the guard is `isRedeemptionBenefit == true && cusRedeemedPrivilegeIdBenefit == null`.

**STILL UNFIXED:** `api/clients/privileges/redeemed-roadside` is **not in ABCB** and not in any repo checked out in the workspace — find its owner and give it the same idempotency guard that `9ce2e4a65` added to ABCB `RedeemptionCaseService.SyncAllDataCustomerAndCustomerRedeemed` (lookup by `RoadSideJobId`, reuse the existing row). ABCB PR #3659 (`bugfix/roadside-sync-empty-failure`, deployed to prod 2026-08-31 13:02 via pipeline `apac-benefit-sync-data-roadside-prod`) fixed a *different* method and did **not** stop this. Deeper fix: a 504 is ambiguous, so RSA should reconcile by `RoadSideJobId` rather than assume nothing happened — and the Benefit call happens *before* the local save, so a timeout always strands.

**Prod access that worked:** RSA MSSQL `rsa-prod.cofpzhamf3ov.ap-southeast-1.rds.amazonaws.com` / `BKKRsa` is reachable **directly**, no tunnel (creds: Secrets Manager `roadside-connection-string` → ROAD_SIDE_PROD). Benefit MySQL is via the user's tunnel on **localhost:3382**, user `benefitAdmin`, db `Aspire` — its password lives in SSM `/abe/codepipeline/apac-benefit-sync-data-roadside-prod/APPSETTINGS_JSON`, which the sandbox refuses to decrypt, so ask the user.

**Error triage on RSA prod:** errors go to `wlib.EventLog` (`EventType='Error'`, `EventName='Exception / jobId: <id>'`, `Details`=`ex.ToString()`). The daily `EventLog_yyyyMMdd` tables stopped in 2024; retention is only ~4 days. **Always filter by `EventType='Error'`** — an open job page polls ~2 rows every 4s and floods any `TOP n` by jobId. Progress markers bracketing the Accept flow: `Key acceptJob`, `GetSaveAcceptFields`, `SaveJobInfo Success / jobId:`.

See [[abe-repo-aliases-and-cms-modules]], [[abmb-roadside-cicd]].
