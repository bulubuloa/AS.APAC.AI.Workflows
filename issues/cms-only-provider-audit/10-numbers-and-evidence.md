# 10 — Numbers and evidence

Everything quoted in documents 00–09 comes from here. Production RSA database (`BKKRsa`, read-only SELECTs), Kontent production environment `994226e6` via the public Delivery API, and the `roadside-release-production` code (`c65a74d1`). Measured 16 Sep 2026.

## Provider counts (RSA prod)

| Query | Result |
|---|---|
| Active providers, `accountId` `1-`/`2-`, `active=1`, not deleted | 719 |
| …of which with a `vendorCmsId` | 712 |
| …of which with `isProviderMobile = 1` | 352 (+1 unlinked) |
| CMS-linked rows (any status) | 783 |
| Active + CMS says mobile=yes + RSA `isProviderMobile` 0/NULL | **317** — `StatusSysnData`: 274 `Success`, 40 `Update From Benefit`, 3 `Create From Benefit` |
| CMS-linked rows whose CMS item is not a roadside vendor | 47 total, 24 active: 5 *Auto Services / Towing Assistance* (`2-0030`, `2-0052`, `2-0073`, `2-0119`, `2-0175`), `1-0004` (empty sub-category), 13 *Home or Business Maintenance*, 1 *Car Rental*, 2 *Health*, 1 unpublished (`2-1870`) |
| Active rows with no `vendorCmsId` | 7: `2-0838`, `2-1662`, `2-1669`, `2-1670`, `2-1802` (mobile=1), `2-1826`, `2-1827` |
| Vehicles | 1,038 rows, 414 providers |

## Job counts (RSA prod)

| Query | Result |
|---|---|
| Jobs last 90 d with a provider, by mode | Auto 8,338 (82 providers) · Manual 5,284 (356 providers) · all on CMS-linked providers |
| Jobs last 365 d | 51,764 — 51,761 CMS-resolvable, 1 CMS-linked-but-outside-filter, 2 non-CMS; 0 with empty stored `provName` |
| Jobs ever assigned to `2-0938` | 0 |
| Job `26JB067586` | `tstampMethod='A'`, clientId 393, TOWING, `accountId` NULL |

## CMS counts (Kontent prod, Delivery API)

| Query | Result |
|---|---|
| `template_generic` items with a module, filtered to *Auto Services* + *Roadside Assistance* and a `module_roadside_assistance` | 752 |
| …`mobile_vendor = yes` | 687 |
| …active + mobile | 651 |
| Vendor `3c22b305-…` (Asia Lue Garage) | status `active`, module `rsa_asia_lue_garage__migrated_`, `mobile_vendor: yes`, item last modified 2026-07-07 |

## Latency (from a laptop in Bangkok, 16 Sep 2026, 3 samples each)

| Call | With `X-KC-Wait-For-Loading-New-Content: true` (what the code sends) | Without |
|---|---|---|
| Single vendor by ID, depth 1 (≈ 20 KB) | 1.04 – 1.58 s | 0.19 – 0.45 s |
| Full `template_generic` list page, depth 0, limit 1000, `module_dynamic_category[nempty]` (≈ 2.2 MB, one page) | 2.38 s | 4.30 s |
| Batch, 50 IDs, depth 0 | ≈ 0.92 s | — |
| `module_roadside_assistance` full list | ≈ 3.9 s | — |

`GetListProvidersAsync` issues four calls in parallel (vendors, modules, groups, countries); wall time ≈ the slowest, 2.4–4.3 s; total download ≈ 2.3 MB. No caching layer exists anywhere in the solution (`grep -i cache BenefitCmsService.cs` → nothing).

## Where the code reads / writes provider data

| Area | File : line (roadside-release-production) |
|---|---|
| Search box | `BkkRsa/Api/AutofillController.cs:49-146`; JS `Scripts/rsa/BkkRsa.Autofill.js:25`; `Views/Msu/Job.cshtml:2720` (`minLength: 0`) |
| Nearest technicians | `BkkRsa.Web/AppCode/Db/Extension/JobInfoExtension.cs:28`; `BkkRsa.Core/AppCode/Models/NearProviderModel.cs:56-175` |
| Job save provider name | `BkkRsa/Api/MswsController.cs:363-382, 977-989`; `MswsController_JobOthers.cs:277` |
| Hand-typed name on benefit jobs | `BkkRsa/Api/MswsController.cs:1027-1046` |
| Benefit vendor ID | `BkkRsa/Api/MswsController.cs:398-406`; `BenefitServices/JobRedeemption/JobRedeemptionHelper.cs:31-37` |
| Job detail overlay | `BkkRsa/Controllers/MsuController.cs:202-222`; `BkkRsa.Core/AppCode/Models/JobInfoModel.cs:183-198` |
| Monitor board | `BkkRsa/Hubs/JobSignalManager.cs:77`; `BkkRsa.Core/AppCode/Model/JobMonitorModel.cs:62-78` |
| Job action list | `BkkRsa/Api/MswsController_JobAction.cs:72`; `JobActionSM.cs:36-41` |
| Customer tracking | `BkkRsa/Api/MswsController_TrackJob.cs:43`; `TrackJobModel.cs:58-61` |
| Map markers | `BkkRsa/Api/MswsController_JobOthers.cs:290-380` |
| Provider list | `BkkRsa/Controllers/ProvUserController.cs:37, 69-143` |
| Provider detail | `BkkRsa/Api/AccountController.cs:162-310` (overlay at 278-296); save at 188-266; reset pwd 328 |
| Provider review | `BkkRsa/Controllers/ProvReviewController.cs:39-62, 103-115` |
| Vehicle screens | `BkkRsa/Controllers/MsuController.cs:660, 751-763, 801-820`; `VinServiceSM.cs:54-60` |
| Login | `BkkRsa/Controllers/Security/AuthController.cs:63-85`; `BkkRsaPartner/Api/PmwsController.cs:240-290, 608`; `BkkRsaProvider/Controllers/AuthController.cs:57-70` |
| Auth filter (active per request) | `BkkRsa.Web/BkkRsa.Web.Mvc/RsaJwtAuthenAttribute.cs:129` |
| Lost-signal timer | `BkkRsa/AppCode/BkkRsa/RsaScheduler.cs:26-31`; `Global.asax.cs:150, 233` |
| Sync v1 | `BkkRsa/Api/ProviderSyncBenefitController.cs:418`, `MapUserAccount:734-745` |
| Sync v2 | `BkkRsa/Api/ProviderSyncBenefitController.cs:494-570` (no `isProviderMobile` / `countryCode` / `email`) |
| Benefit-side v2 payload | `ABVB VendorServerless.Shared/Requests/ProviderRoadside.cs:27-42`; `VendorService.cs:3204-3225` |
| Delete provider | `ProviderSyncBenefitController.cs:767, 994` |
| Reports | `BkkRsa/Controllers/ReportController.cs:35 (Compass), 142 (Complete), 249 (JobInfo, overlay 311-341), 488 (JobDetail)`; `BkkRsa.Core/AppCode/Model/CompleteReportModel.cs:121-139`; `BkkRsa.Report/JobReportModel.cs:51-59`; `CompassReportModel.cs:81-85` |
| CMS client | `BkkRsa/BenefitServices/BeneifitCms/BenefitCmsService.cs:73-220 (list), 223-236 (by id), 365-440 (detail)`; roadside filter at 129-131; env default at 98 and 374 |
| Environment config | `KontentEnvironmentId` app setting; SIT/pre-prod unset → default `994226e6` |

## Queries used (all read-only)

```sql
-- provider counts
SELECT linked = CASE WHEN vendorCmsId IS NULL THEN 'no' ELSE 'yes' END, COUNT(*), SUM(CASE WHEN isProviderMobile=1 THEN 1 ELSE 0 END)
FROM cloud.UserAccount WHERE (accountId LIKE '1-%' OR accountId LIKE '2-%') AND active=1 AND ISNULL(isDelete,0)=0
GROUP BY CASE WHEN vendorCmsId IS NULL THEN 'no' ELSE 'yes' END;

-- all CMS-linked rows (diffed in Python against the Kontent list)
SELECT accountId, dispName, active, isDelete, isProviderMobile, vendorCmsId, StatusSysnData, dtModify
FROM cloud.UserAccount WHERE vendorCmsId IS NOT NULL AND (accountId LIKE '1-%' OR accountId LIKE '2-%');

-- jobs by mode, last 90 days
SELECT j.tstampMethod, COUNT(*), COUNT(DISTINCT j.accountId)
FROM cloud.JobInfo j JOIN cloud.UserAccount u ON u.accountId=j.accountId
WHERE j.dtInsert >= DATEADD(day,-90,GETDATE()) GROUP BY j.tstampMethod;

-- jobs by provider, last 365 days
SELECT accountId, COUNT(*), SUM(CASE WHEN provName IS NULL OR provName='' THEN 1 ELSE 0 END)
FROM cloud.JobInfo WHERE dtInsert >= DATEADD(day,-365,GETDATE()) AND accountId<>'' GROUP BY accountId;

SELECT COUNT(*), COUNT(DISTINCT accountId) FROM cloud.Vehicle;
```

```
# Kontent (no key needed for this project's Delivery API)
GET https://deliver.kontent.ai/994226e6-d1a5-023e-0fc9-21571d884f47/items?system.type=template_generic&depth=0&limit=1000&elements.module_dynamic_category[nempty]
GET https://deliver.kontent.ai/994226e6-.../items?system.type=module_roadside_assistance&depth=0&limit=1000
GET https://deliver.kontent.ai/994226e6-.../items?system.type=template_generic&system.id[in]=<id>&depth=1&limit=1
```
Joined in memory on `elements.module_dynamic_category[]` → module codename → `elements.mobile_vendor[].codename == "yes"`, with `category_text` / `sub_category_text` / `vendor_status` from the vendor item.
