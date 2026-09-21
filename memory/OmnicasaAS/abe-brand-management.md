---
name: abe-brand-management
description: "RSA Brand Management (~/admins/brand) — 255-char brand name split (ABE-5341), hide Delete when in use, file map, deploy state"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9d5486f7-6f25-4ff6-a72b-e38c632ec649
  modified: 2026-08-25T04:44:14.290Z
---

RSA Brand Management lives in ABMB `bkkrsa2020-master` (see [[abe-repo-aliases-and-cms-modules]], [[abmb-kontent-env-switch]]): `Areas/Admins/Controllers/BrandController.cs`, `Areas/Admins/Views/Brand/{Index,Form}.cshtml`, service `BkkRsa/BenefitServices/BeneifitCms/BrandCmsService.cs`, models `BkkRsa/Models/Brand/BrandModels.cs`. Brands/models are Kontent items (`vehicle_brand`/`vehicle_model`); ALL reads map the `name` ELEMENT, never the item name.

**ABE-5341 (2026-08-25): brand name max = 255.** Kontent caps a content ITEM name at 200 (platform hard limit, cannot be raised) → split: item name trimmed to 200 (`TrimToItemName`), `name` element keeps full 255 (`TrimTo(m.Name, BrandNameMax)`). Form maxlength 255, controller trims at 255. CMS type needs NO change (no `maximum_text_length` on the text elements — verified via Mgmt API). Benefit/ABF has no vehicle-brand code (its "brand" = website branding). DB: `cloud.JobInfo.brand` was nvarchar(100) → widened to 255 + `sp_refreshview cloud.VW_JobInfo` (**applied on BKKRsaStaging 2026-08-25**; script `Sql-scripts/20260825_ABE-5341_Brand255_JobInfo.sql`. **VERIFIED APPLIED ON PROD 2026-08-31** - `cloud.JobInfo.brand` is nvarchar(255) on rsa-prod, shipped in section 5 of `20260828_MASTER_PreDeploy.sql`) + EDMX `BkkRsa.Core/Db/BkkRsaModel.edmx` brand MaxLength 100→255 in 4 spots. **Model names still cap at 200 everywhere** (`carModel` is nvarchar(30)!) — same split pattern applies if QA extends the ask.

**Hide-Delete-when-in-use (2026-08-25, no ticket id given):** brand list Delete button hidden per row via `BrandListItem.InUse`, set in `BrandController.Index` from new `BrandCmsService.BrandNamesInUse` (one SQL IN query per page; shared `NamesInUse(column,...)` with `ModelNamesInUse`). Form model rows: `renderModels()` skips the Delete button when `inUse(name)` (ABE-5342 alert + server-side drop-refusal kept as backstops). "In use" = some `cloud.JobInfo` row carries the exact trimmed name (case-insensitive).

**Deploy state:** all of the above is local-only code (UAT DB part applied live); needs push to Bitbucket `roadside-release-uat` (user pushes) + `roadside-backend-uat` pipeline. No new files → no .csproj edits needed.
