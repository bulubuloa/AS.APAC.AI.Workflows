---
name: reference-dataprocesser-uat-pipeline
description: AWS UAT deployment topology for DataProcesser (TPI) — new compute env + queue + S3 EventBridge rule; and the hardcoded-clientId latent bug in cloned processors. Use when adding UAT for a client or when a cloned client works in prod but not UAT.
metadata: 
  node_type: memory
  type: reference
  originSessionId: 571ff252-ee96-4af2-bc87-215ae21f6d68
---

## DataProcesser UAT topology (ap-southeast-1, acct 739075353953)

UAT for the modern shared-image processor (`apac-benefit-data-processer-*`) did NOT exist before TPI. Built for TPI (ABE-5104):
- **Compute env**: `benefit-import-data-clients-uat` (FARGATE clone of `benefit-import-data-clients-preprod` — same subnets/SGs, AWSServiceRoleForBatch).
- **Job queue**: `benefit-import-uat-job-queue` → that CE. NOTE: account is at the hard **50 job-queue limit**; freed a slot by deleting the decommissioned `benefit-import-ktc-preprod-job-queue` (its rule `benefit-import-data-clients-ktc-preprod` was also DISABLED — dangling but harmless).
- **Job def**: `benefit-tpi-import-uat-job-definitions` — reuses the preprod ECR image (env-agnostic; reads `CONNECTION_TARGET`). Rev 2 = `apac-benefit-data-processer-pre-production:tpi-v1.1`.
- **Rule**: `tpi-uat-email-rule` — S3 `benefit-raw-email-receiving` prefix `uat/EMAIL/TPI/` → UAT queue, job def revision-pinned ARN, InputTransformer injects `CONNECTION_TARGET=UAT`, `JOBTYPE=CLIENT_TPI_DATA_PROCESSER`, `CLIENT_NAME/CODE=TPI`, RECIPIENT/CC emails. Same revision-ARN + InputTransformer rules as preprod ([[reference-dataprocesser-preprod-pipeline]]).

UAT DB: secret `benefit-connection-string-preprod` key `connectionStringBenefitUat` → cluster `benefit-sit...rds` db `AspireProdBackup` (dev tunnels it to localhost:3374, uid admin). Input S3 object is a raw **MIME email (.eml)**; processor extracts the .xlsx attachment via MimeKit (not a bare xlsx).

## Latent bug: hardcoded ClientId breaks non-prod envs

Cloned processors (TRI, TPI, …) resolve customers/field-configs by `ClientCode` but hardcode the program lookup: `programs.ClientId == {CLIENT}Constants.CLIENT_ID_EXTERNAL` (a PROD clients.Id, e.g. TPI=105). Client Ids are env-specific ([[reference-masterdata-ids-env-specific]]) — UAT TPI is Id **470** — so the query finds no program, `programTier` is null, and the import silently produces nothing. Fix (TPIBatchProcessor): resolve `clientId` from `ClientCode` once (mirror `LoadFieldConfigs` join), fall back to the constant. TRI has the same latent bug (works in prod only because prod Id matches).
