---
name: reference-csm-uat-pipeline
description: "How CSM (Chubb Samaggi, ABE-5384) is deployed and configured on UAT — job def resolved by NAME via the test-drop tool, image tag convention, and the masterdata-parent gotcha when changing a field's data type by SQL."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 3002fc97-35fc-4a9d-be27-f35866fe73e5
  modified: 2026-09-16T10:12:25.876Z
---

CSM UAT (as of 2026-09-16), branch `jira/ABE-5384-CSM-chubb-samaggi`:
- Image: `apac-benefit-data-processer-pre-production:uat-abe5384-csm-YYYYMMDD-NN`, built from `DataProcesser/Dockerfile` (`--platform linux/amd64`).
- Job def `benefit-csm-import-uat-job-definitions` — **no EventBridge rule**; the QA test-drop Lambda submits it by NAME, so registering a new revision (copy latest revision's containerProperties, swap image) is the whole deploy. Rev 5 = 20260916-01, rev 6 = 20260917-01 (AddressEn core column fix).
- Files: bucket `sftp-aspirelifestylesasia-com`, root `chubb/chubb_uat`, subfolders `CHUBB_AH` / `CHUBB_MOTOR`; processor tries both.
- UAT DB via tunnel localhost:3375, creds from secret `benefit-connection-string-preprod` key `connectionStringBenefitUat`; `pymysql` is installed, no `mysql` CLI. Auto-mode blocks UAT writes — give the user a short `~/x.py` command to run (long paths wrap in the prompt and split the argument off).

**Gotcha:** on UAT the `Customer_Attribute_DataType` masterdata row has a non-NULL `ParentId`, so a `... AND ParentId IS NULL` lookup returns NULL and an UPDATE silently sets `DataTypeId = NULL`. Resolve ENUM etc. by joining child→parent on MasterCode only ([[reference-masterdata-ids-env-specific]]). UAT ENUM id = 50598.

QA config changes for CSM (16 Sep): PackageType ENUM/SINGLE Silver|Gold|Copper|Legacy; Motor feed allows only Silver/Gold (enforced in CSMRowValidator). Prod needs the same SQL (`database/Sprint63/ABE-5384_CSM_PackageType_enum.sql`) at release.
