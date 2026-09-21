---
name: reference-kontent-envs-brand-module
description: Kontent.ai environment IDs + where the Management API keys live for the RSA Brand & Model module (prod vs staging/SIT)
metadata: 
  node_type: memory
  type: reference
  originSessionId: 184db21a-bd5c-494f-acc2-425a2bf1ac6a
  modified: 2026-08-17T15:17:37.911Z
---

Vehicle Brand/Model for RSA (`vehicle_brand`, `vehicle_model`, `engine_system`, `defect_issue` content types) lives in **Kontent.ai**, project `7dd2a4d8-528c-02b6-8240-b747a0d5a79c`:

- **prod** env `994226e6-d1a5-023e-0fc9-21571d884f47` — key in SSM `/abe/codepipeline/apac-benefit-vendor-backend-prod/APPSETTINGS_JSON` → `ManagementOptions.ApiKey`
- **staging/SIT** env `225b0999-fce9-02b4-c44b-ed6990faeeaa` — key in SSM `/abe/codepipeline/apac-benefit-vendor-backend-sit/APPSETTINGS_JSON`

pre-prod shares the **prod** env, so writing "pre-prod" writes production content. There is no vendor-backend-uat pipeline; UAT/SIT of the *client* backend points at a different project (`554d1073-…`) — not the brand data.

`BrandCmsService` (ABMB `RoadSide/bkkrsa2020-master/BkkRsa/BenefitServices/BeneifitCms/`) reads `KontentEnvironmentId` from Web.config and **defaults to the prod GUID** when the setting is absent — Web.config is gitignored, so a misconfigured staging box silently writes prod.

Management API tolerates ~ a few hundred writes before 429; batch item create+variant+publish loops need retry/backoff (a 429 on publish leaves the item created but unpublished, so it disappears from the Delivery API).

Related: [[reference-masterdata-ids-env-specific]]
