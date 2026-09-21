---
name: abe-5457-provider-mobile-flag
description: ABE-5457 Auto-mode provider autocomplete misses CMS-synced providers — Ver2 sync never writes isProviderMobile; 317 prod rows affected (verified 2026-09-16)
metadata: 
  node_type: memory
  type: project
  originSessionId: 2db552b7-d225-4bc9-ab27-0b05624b15d5
  modified: 2026-09-16T02:40:30.755Z
---

ABE-5457 (Bug, Major, 2026-09-16): provider `2-0938` Asia Lue Garage missing from the Provider autocomplete when job Timestamp Mode = A (Auto); visible in Manual. Prod job 26JB067586 (clientId 393, TOWING, providerId still NULL).

**Root cause (code + DB verified):** `AutofillController.ProviderName` filters `ua.isProviderMobile == true` in mode A (both the RSA-name path and the CMS→vendorCmsId path go through `baseQuery`), but `ProviderSyncBenefitController.ProviderSyncDataVer2` never writes `isProviderMobile` (only v1 `MapUserAccount` does), and ABVB `ProviderRoadsideVer2`/`VendorRequestVer2` carry no mobile field — the flag lives only in Kontent `module_roadside_assistance.mobile_vendor`. The provuser edit page (`AccountController.cs:296`) overlays the CMS value, so the screen says "Mobile Provider" while the column is 0/NULL.

**Prod numbers 2026-09-16:** 783 CMS-linked RSA providers; 317 are CMS mobile=yes + active on both sides but RSA `isProviderMobile` 0/NULL (274 StatusSysnData 'Success' = migrated, 40 'Update From Benefit', 3 'Create From Benefit'). CMS prod has 752 roadside vendors, 687 mobile=yes — many call-centre vendors (BMW/Toyota/Nissan Call Center) are mobile=yes in CMS, so a blanket backfill needs BA sign-off on which store is master. 2-0938 has never been dispatched a job (not a regression).

**Done 2026-09-16 (branch `jira/ABE-5457-provider-mobile-flag` off `roadside-release-production`, commit 3a0545a0, NOT pushed — user pushes):** `ProviderSyncDataVer2` now does one `ProviderDetailCMS` lookup (`ProviderCmsOrNullAsync`) and writes isProviderMobile/countryCode/email via `ApplyCmsFlags` on create+update; `AutofillController` path (b) uses the unfiltered `scope` so CMS-matched rows skip the RSA mobile gate. Backfill script `Sql-scripts/20260916_ABE-5457_BackfillProviderMobileFlag.sql` (317→1, 10→0, staged with backup table `cloud.ABE5457_isProviderMobile_backup` + rollback) must wait for BA review of `issues/ABE-5457-mobile-flag-review.md` (9 call-centre-looking vendors flagged). Not built locally (net48, Windows CI only). The wider CMS-only audit lives in `issues/cms-only-provider-audit/` (34 md, 73 mermaid) + Lambda reader `cms-only-provider-audit-docs` (ap-southeast-1, public URL zyd5wnrzds2cwzqpfyr6gsajqe0vzlpc) — deferred by user.

**Original fix direction:** RSA `ProviderSyncDataVer2` reads `mobile_vendor` via `ProviderDetailCMS(vendorCmsId)` (same pattern as `NoteFromCmsAsync`) on create+update; optionally let autofill path (b) trust the CMS flag; then a CMS-driven backfill of the 317 rows (list in that session's scratchpad `affected.csv`).

**Access recipe that worked:** `aws secretsmanager get-secret-value --secret-id roadside-connection-string ... | node q.js ROAD_SIDE_PROD file.sql` (creds via stdin, never on disk) + public Kontent Delivery `https://deliver.kontent.ai/994226e6-.../items?system.type=template_generic&depth=0&limit=1000&skip=N` (no key). See [[abe-5320-porsche-dealer-sync]], [[abmb-roadside-cicd]].
