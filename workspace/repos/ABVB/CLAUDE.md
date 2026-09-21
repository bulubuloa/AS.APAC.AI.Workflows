# apac-benefit-vendor-backend (ABVB) — Vendor backend

- .NET Lambda (`VendorServerless`, shared models in `VendorServerless.Shared`). Branches `develop` (SIT) → `staging` (UAT) → `main` (PROD); a second Lambda `apac-benefit-sync-data-roadside-*` deploys from `roadside-sync-data-{uat,prod}`.
- Owns vendors and their Kontent.ai CMS modules (`CmsService`, `Models/KontentAICMS/*`, `ConstKontentAICMS.ContentTypeCodename`, `VendorConstants.ModuleCodename`), and the vendor/dealer → RSA sync (`ProviderRoadsideVer2`, `VendorRequestVer2`, dealer sync keyed on client code; Porsche dealer sync ABE-5320 with the two-brand gate).
- Kontent.ai keys in SSM `/abe/codepipeline/apac-benefit-vendor-backend-{sit,prod}/APPSETTINGS_JSON`; there is no vendor-backend-uat pipeline (SIT config serves UAT). Management API rate-limits after a few hundred writes — batch loops need retry/backoff; a 429 on publish leaves an item created but unpublished.
- Brand names: Kontent item name caps at 200 chars while the element allows 255 — split accordingly (ABE brand management).
- Vendor group codenames (e.g. `porsche_rsa`) must exist and be published in `vendor_group_list` in the target env before dealers can sync.
- Vendor deactivation must propagate to RSA `cloud.ClientDealer.bActive` (ABE-5322).
