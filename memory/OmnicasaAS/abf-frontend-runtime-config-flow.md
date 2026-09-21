---
name: abf-frontend-runtime-config-flow
description: How ABF (benefit frontend) loads runtime config in UAT/SIT/prod — where SiteLoungePass etc. actually live
metadata: 
  node_type: memory
  type: reference
  originSessionId: fcf92be1-1fb8-4a5b-b2c0-8404944c9cab
---

ABF (apac-benefits-frontend, repo bitbucket internationalsos/apac-benefits-frontend) does NOT read its
S3 `appsettings.json` at runtime in non-dev. In `src/Client/Program.cs`, non-dev calls
`GetParameterStore.GetAppsettingFromServerSide(domain)` → `GET https://api-benefit-<env>.aspireasia.net/api/clients/parameter-store/get-parameter-store`
→ AES-CBC encrypted blob (key + iv are the constants in `src/Client/Program.cs`, PKCS7) → decrypted client-side into IConfiguration.

The client-backend (ABCB = Omnicasa.Mobile.ABCB) serves that endpoint. Its appsettings come from
Secrets Manager `codepipeline/apac-benefit-client-backend-<env>/APPSETTINGS_JSON`. The frontend
ApplicationSettings it returns are read LIVE from the SSM SecureString named by
`ServiceConfiguration.ParameterStoreAppConfigFrontend` = **`/abe/codepipeline/apac-benefit-frontend-<env>/APPSETTINGS_JSON`**
(note: `apac-benefit-...`, not `apac-benefits-...`).

So to change a frontend config value (SiteLoungePass, SiteLimo, BaseAddress, ApiKey, Okta, FeatureFlags…)
for UAT: edit SSM SecureString `/abe/codepipeline/apac-benefit-frontend-uat/APPSETTINGS_JSON` (key
`alias/aws/ssm`, ap-southeast-1), JSON `ApplicationSettings` section, `put-parameter --overwrite`.
NO redeploy needed — backend reads SSM per request (verified live). Decrypt-to-verify: call the endpoint,
base64-decode, AES-CBC decrypt with the key/iv from Program.cs.

The S3 bucket `apac-benefits-frontend-uat` `appsettings.json` is a DEAD red herring: bucket policy has an
explicit `Deny s3:GetObject Principal:*` on that exact key, so CloudFront (distro EEG9N53J48U2O) 403s →
custom-error-response rewrites to /index.html. Editing it changes nothing. Don't waste time there.

ABE-4929 (Lounge Pass blank on UAT): root cause was SiteLoungePass missing from this UAT SSM param (SIT had it).
Fits the recurring env-drift theme [[abe-repo-aliases-and-cms-modules]] — SIT has config UAT/prod lack.
Check prod `/abe/codepipeline/apac-benefit-frontend-prod/APPSETTINGS_JSON` for the same gap.
