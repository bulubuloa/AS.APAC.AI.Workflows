---
name: abe-4681-vehicle-fields
description: "ABE-4681 RSA Job vehicle fields (Brand/Model/Engine System/Defect Issue) — impl state, CMS types, pending deploy steps"
metadata: 
  node_type: memory
  type: project
  originSessionId: ad9d2251-4c72-43f8-87c1-d562caa07dfc
  modified: 2026-08-05T03:27:58.179Z
---

ABE-4681 "Add Vehicle Information Fields for RSA Jobs" (13 SP) — implemented in ABMB RoadSide (bkkrsa2020-master) on 2026-07-23. Adds Brand + Engine System (new) and repoints Model(carModel) + Defect Issue from RSA DB → CMS. All 4 stored as name strings on cloud.JobInfo, shown as dependent searchable autocompletes: Client→Brand→Model→(Engine System|Defect Issue). See [[abe-repo-aliases-and-cms-modules]].

**Decisions (from user):** I create+seed CMS types via Mgmt API; Defect Issue = single GLOBAL list; migration = preserve existing carModel/defectIssue text, new fields blank.

**OUTDATED as of 2026-08-04: UAT now reads Kontent env `225b0999`, not 994226e6 — see [[abmb-kontent-env-switch]].**

**CMS (Kontent env 994226e6, the env the RoadSide app read until 2026-08-04) — DONE:** created content types `engine_system` and `defect_issue` (each element `name` text) via Management API; seeded+published engine systems ICE/EV/HEV/PHEV AND all 14 defect_issue items (English (Thai) - BAxx format, from distinct cloud.UC_DefectIssue). Mgmt key lives in SSM `/abe/codepipeline/apac-benefit-vendor-backend-pre-prod/APPSETTINGS_JSON` → `ManagementOptions.ApiKey`. Seed script: scratchpad `abe4681_cms_seed.py` (idempotent; `python3 abe4681_cms_seed.py defects.txt`).

**UAT RSA DB access (for future ops):** DB = `BKKRsaStaging` on apac-staging RDS. The box's Web.config `BkkRsaConString` lacks the password (app decrypts SecureConString at runtime). Working apacadmin creds are in SSM `/abe/codepipeline/apac-benefit-sync-data-roadside-uat/APPSETTINGS_JSON` → `ConnectionStrings.BKKRSA` (has server+db+user+password inline). The box (i-0c0b0ffcdfec95d6f) can reach RDS 1433 + read that SSM param itself, so run SQL via SSM RunPowerShellScript from the box. NOTE: RDS gets stopped/started (was down once), verify TCP1433 first.

**Gating gotcha:** jobApp `getModel()` uses `serializeJSON()` which DROPS `disabled` inputs, and server `WriteModel` only writes keys present in the payload. So the form gates the 4 fields with `readonly` (+ `.vf-gated` grey class), NOT `disabled` — readonly still serializes, so migrated carModel text is never null-wiped. Downstream values cleared only on user upstream change.

**VW_JobInfo REGRESSION (found+fixed 2026-07-27):** The 2026-07-23 migration's ALTER VIEW was based on the OLD repo `Cloud Db v1.6.x` body and DROPPED ~14 live columns from cloud.VW_JobInfo (cmFName,cmLName,cemail,clientProgram,cusRedeemedPrivilegeIdBenefit,isRedeemptionBenefit,dtSyncBenefit,ProgramCusTiersBenefit,privilegeIdBenefit,ProductIdBenefit,clientTargetId,clientTargetName,technicianCost,freeWheel,riskCase). Broke MsuController.JobLst (SQL err 207 "Invalid column name 'cmFName'") — surfaced as "user jessie.tahongloan can't access" (she HAS R0001; it was the Job List erroring, not the menu). Fix: pulled the intact view def from **BKKRsaPreprodLite** (preprod, same RDS `apac-staging`, not ABE-4681-migrated) via `OBJECT_DEFINITION`, re-ALTERed UAT with it + brand/engineSystem. Repo script now corrected. LESSON: never rebuild a view from old repo SQL — extract the live def from preprod/prod first. RSA app errors are logged to `wlib.EventLog` (Details=ntext, cast to nvarchar(max)); menu gate = `User.IsInRole("R0001")` from UserAccount.roles.

**Failed Testing 2026-07-29 (Mia) — root cause found:** "Brand field shows no brands for client COF (clientId 1957)". UAT IIS log `C:\inetpub\logs\LogFiles\W3SVC16\u_ex260729.log` shows `GET /msu/brands/1957 -> 404`. Cause: `Controllers\MsuController_VehicleFields.cs` was never added to `BkkRsa.csproj` (old-style .NET Framework project = explicit `<Compile Include>`), so all 4 endpoints (brands/brandmodels/enginesystems/defects) don't exist in the deployed dll. CMS + DB data were fine (COF owns "Harley division" + "SnapGlow"). Fixed: added the Compile entry + made the 4 autocompletes open the full list on focus/click (jQuery UI minLength:0 alone only opens while typing, which QA reads as "no list"). LESSON: any new .cs in this repo must be hand-added to the .csproj; a 404 on a brand-new RSA endpoint = check csproj first. Deployed view files are Razor (runtime-compiled) so they ship even when the code doesn't — Job.cshtml md5 matched local while the dll lacked the controller.

**Deploy steps:** (1) DONE — ran SQL `BkkRsa/Sql-scripts/20260723_ABE-4681_AddBrandEngineSystem_JobInfo.sql` on BKKRsaStaging (UAT); verified cloud.JobInfo.brand+engineSystem and VW_JobInfo expose them. VW_JobInfo re-fixed 2026-07-27 (see regression note above). (2) DONE — defect_issue seeded. (3) TODO build+deploy app to UAT (roadside-backend-uat pipeline, see [[abmb-roadside-cicd]]). KontentManagementApiKey + KontentEnvironmentId already in the UAT box Web.config (permanent, never overridden — from ABE-5164). (4) TODO push commit (Bitbucket — user must push). Prod: re-run the SQL on prod DB + verify defect_issue/engine_system exist in the prod env before prod deploy.

**Files:** entity BkkRsa.Core/Db/JobInfo.cs; EDMX BkkRsaModel.edmx (7 spots); save whitelist BkkRsa.Core/AppCode/Db/JobInfo.cs; CMS reads BkkRsa/BenefitServices/BeneifitCms/BrandCmsService.cs + Models/Brand/BrandModels.cs; endpoints BkkRsa/Controllers/MsuController_VehicleFields.cs (/msu/brands,brandmodels,enginesystems,defects); form BkkRsa/Views/Msu/Job.cshtml; export CompleteReportModel.cs + ReportController.cs headerMapping. Old /msu/carmodel + /msu/defectissue endpoints left in place but unused by the form.
