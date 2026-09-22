---
name: rsa-benefit-backend-topology
description: "Where the RSA (BkkRsa) app's \"Benefit\" backend endpoints actually live (repo/service/branch)"
metadata: 
  node_type: memory
  type: reference
  originSessionId: fc8ab534-1769-4791-8374-09271e4e7712
---

The RSA app (`ABMB`, project `RoadSide/bkkrsa2020-master/BkkRsa`) is a thin pass-through: privilege/program/redemption data comes from a backend configured as the `BenefitWebHookEndPoint` app-setting (not committed — injected at deploy from AWS SSM Parameter Store, region `ap-southeast-1`).

That backend is the **`ABCB`** repo (namespace `ClientService.*`). It deploys as several Lambda microservices (SSM path `/abe/codepipeline/apac-benefit-*`):
- `apac-benefit-client-backend` → project `ClientService.API` (serves `api/clients/privileges/...`, e.g. `roadside-eligible-services`). Branch `develop` has the **new ABE-4612 taxonomy logic** (`RoadsideEligibleProductService`, `ProductTaxonomyMatcher`, `ProductAdditionMethod`, rules matching).
- `apac-benefit-sync-data-roadside` → project `WebHookSyncDataRsaBenefit` (serves `api/webhook-roadside/...`, including `ProgramPrivilege/get-privileges-by-programid` which fills the RSA Job privilege dropdown). Deployed from branches `roadside-sync-data-{sit,uat,prod}`. This project is on an **older schema** — `Privilege` has NO `ProductAdditionMethod`, no rules/matching, no taxonomy matcher.

RSA-eligible roadside taxonomy (per ABE-4612): Category `AUTO` + Sub-Category `ROADSIDE` + ProductType code in {REPAIR, BATTERY, BATREPL, GASOLINE, HOME, LOCK, TOWMOTOR, TOWING, TYRE}. Product entity maps category=`ServiceId`, subcategory=`ServiceChildId`, type=`ProductType` → join `MasterDatas` for `MasterCode`. See [[abe-4612-privilege-name-bug]].
