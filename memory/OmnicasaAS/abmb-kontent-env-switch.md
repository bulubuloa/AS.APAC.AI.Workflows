---
name: abmb-kontent-env-switch
description: ABMB RSA UAT Kontent env switched to 225b0999 (2026-08-04); the 4 RSA-authored content types must be replicated on any env switch + >200-char brand name create bug
metadata: 
  node_type: memory
  type: project
  originSessionId: c5cdd69f-7c80-4ecf-8fed-d5a03ac28889
  modified: 2026-08-05T03:27:45.582Z
---

**UAT RoadSide now reads Kontent env `225b0999-fce9-02b4-c44b-ed6990faeeaa`** (switched 2026-08-04 17:21 in `C:\roadside-uat-aspireasia.net\Web.config`; pre-change copy kept as `Web.config.bak-kontentenv` with the old `994226e6-d1a5-023e-0fc9-21571d884f47`). Supersedes the "994226e6 is the env the RoadSide app reads" claim in [[abe-4681-vehicle-fields]]. SIT/preprod Web.configs have NO Kontent keys, so they still use the code default 994226e6 (`BrandCmsService.cs:27`, `BenefitCmsService.cs:73/269/354`).

**The gotcha:** the 4 RSA content types (`vehicle_brand`, `vehicle_model`, `engine_system`, `defect_issue`) were hand-created via the Management API and exist ONLY in envs we made them in — they are NOT part of the Benefit CMS's own type set. Every other type the app reads (`template_generic`, `module_roadside_assistance`, `vendor_group_list`, `country_list`, `roadside_assistance_vehicle_list`) exists in every env. So **any Kontent env switch silently breaks Brand Management + the RSA job vehicle fields** until the 4 types are replicated: Save shows "Saved brand unsuccessfully." (Mgmt `POST /items` → 400) and the Brand list / job autocompletes go empty with NO error banner (Delivery returns 200 with 0 items). The Mgmt API key is project-container-scoped, not env-scoped — it keeps working across envs, so a 400/404 here is never an auth problem.

**Fixed 2026-08-05:** replicated all 4 types + migrated 49 items (9 brands / 22 models / 4 engine systems / 14 defect issues, links+ownership+owner_clients intact) into 225b0999. Reusable idempotent script: scratchpad `abe_kontent_env_migrate.py` (`--apply`, else dry run; reads key from sibling `.kontent_key`). Prod will need the same treatment if it ever moves env.

**Latent bug found (NOT yet fixed):** Kontent caps a content ITEM's name at 200 chars but `BrandController.SaveForm` truncates to 255 (`BrandController.cs:158`) and passes it straight to `POST /items`, so creating a brand with a 200-255 char name always 400s → "Saved brand unsuccessfully"; editing an existing brand to that name works (edit only PUTs the variant, never renames the item). Explains the 07/29 400s in `wlib.EventLog`. Fix = send `name[:200]` as the item name, keep the full value in the `name` element.

**Debug recipe:** RSA errors → `wlib.EventLog` on `BKKRsaStaging` (columns `dtLog`/`EventName`/`Details`; NOT `CreatedDate`), query from the UAT box via SSM using creds in SSM `/abe/codepipeline/apac-benefit-sync-data-roadside-uat/APPSETTINGS_JSON` → `ConnectionStrings.BKKRSA`. See [[abmb-roadside-cicd]].
