---
name: reference_abf_sit_vs_uat
description: "ABF defaults to the SIT API, whose DB lacks some clients (AOI/MIT) — verify Data Processor Report work on benefit-uat, not benefit-sit"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 86277fe9-ddf1-46c1-8f4e-68cd2852bde6
  modified: 2026-09-08T04:02:58.177Z
---

ABF's checked-in `src/Client/wwwroot/appsettings.json` points at `https://api-benefit-sit.aspireasia.net/`;
only `appsettings.Development.json` uses `api-benefit-uat`. **SIT and UAT are different databases**, and
the SIT one (524 clients as of 2026-09-08) has HOT/MBZ/HOG but **no AOI and no MIT** — only a test row
`Mit2026 / "Mit client"` (id 500). On UAT both are live: AOI client 347, MIT client 251.

Symptom that cost an hour: "client not found in the autocomplete" on the Data Processor Report screen.
Neither the page nor `HandbackService` has a client whitelist — the dropdown is `api/clients/get-all-short-info`
(all clients, filtered only for AME/SDA/PDE roles; Administrator sees everything), so a missing client
means the client record does not exist in the environment ABF is pointed at.

`HandbackService.GetRunsAsync` lists the S3 prefix `{ClientCode}/{Environment}/` in bucket
`aspire-dataprocessor-handback-report`, where `Environment` is the API's own setting and the folder was
written from the batch job's `ENV`. No client has a `SIT/` folder — every run folder is `{Client}/UAT/`.
So report work can only be verified on **benefit-uat**, never benefit-sit, regardless of onboarding.

Quick check without a login (the API key in ABF's appsettings gets through the SIT gateway):
`curl -H "x-api-key: <key>" https://api-benefit-sit.aspireasia.net/api/clients/get-all-short-info`.
See [[project_uat_is_dev_environment]] and [[reference_mit_uat_pipeline]].
