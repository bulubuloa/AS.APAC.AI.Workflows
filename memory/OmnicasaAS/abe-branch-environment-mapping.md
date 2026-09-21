---
name: abe-branch-environment-mapping
description: Which git branch deploys to which ABE/benefit environment (SIT vs UAT) and how deploys are triggered
metadata: 
  node_type: memory
  type: project
  originSessionId: 9e10b612-64e4-4c87-8ccf-51e9056f3aea
---

ABE / benefit platform branch → environment mapping (confirmed by hoangqs, 2026-06-26):

- **`develop` → SIT**
- **`staging` → UAT**  (the AWS pipelines named `*-uat` pull their source from the `staging` branch)

So to land a fix in an environment, merge the feature branch into that env's branch, then deploy:
- SIT: merge → `develop`
- UAT: merge → `staging`

Deploys are AWS **CodePipeline** (not direct CodeBuild). Manual run = `aws codepipeline start-pipeline-execution --name <pipeline>`. Key pipelines:
- `apac-benefit-frontend-uat` (ABF frontend, source repo internationalsos/apac-benefits-frontend)
- `apac-benefit-vendor-backend-uat` (ABVB VendorServerless)
- `apac-benefit-identity-backend-uat` (ABIB identity), `apac-benefit-client-backend-uat`, etc.
Lambda deploy config lives in SSM under `/abe/codepipeline/<pipeline-name>/...`; the ABVB buildspec resolves it via `${CODEBUILD_INITIATOR}`, so it MUST be started by the pipeline (starting CodeBuild directly as an IAM user resolves the wrong SSM path).

Caveat: the identity API JWT signing secret is hardcoded in source (`CurrentUserService`/`UserServices`) and shared across envs, so a valid-signature token from one env passes signature checks in another. See [[abe-repo-aliases-and-cms-modules]].
