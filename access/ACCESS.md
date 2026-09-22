# Access recipes (no secrets in this file — only where they are)

AWS account `739075353953`, region `ap-southeast-1`. Access is an **IAM user** (console sign-in at
`https://ap-southeast-1.signin.aws.amazon.com/`, not Identity Center). For the CLI: console -> your name -> *Security credentials* ->
*Create access key* (CLI), then `aws configure` (key, secret, `ap-southeast-1`, `json`). Keys live only in `~/.aws/credentials`.
`aws sts get-caller-identity` must show that account. If *Create access key* is not allowed, an AWS admin creates it for your user.

## Databases

The RDS endpoints are VPN-gated; the developer opens SSH tunnels on fixed local ports and the agent connects to
`127.0.0.1:<port>`. Ports are a convention shared with the memory notes — keep them.

| Local port | Target | Schema(s) | Login |
|---|---|---|---|
| 3375 | Aurora MySQL cluster `benefit-sit` | `Aspire` = **SIT**, `AspireProdBackup` = **UAT**, `BenefitPreProdV3`, `AspireSITCopy`, `EPassSIT/UAT`, booking DBs | admin: secret `benefit-connection-string-preprod` → key `connectionStringBenefitUat` (host/user/password inside). App logins: SSM `/abe/codepipeline/apac-benefit-client-backend-{sit,uat}/APPSETTINGS_JSON` → `ConnectionStrings.Aspire` |
| 3374 | older alias of the same cluster used in some notes | `AspireProdBackup` | same |
| 3382 | Aurora MySQL `benefit-prod` — **SELECT only** | `Aspire` | secret `benefit-connection-string-preprod` → `connectionStringBenefitProduction` (user `benefitAdmin`); also SSM `/abe/codepipeline/apac-benefit-client-backend-prod/APPSETTINGS_JSON` |
| 3383 | RSA MSSQL `rsa-prod` (also reachable directly from the VPN) | `BKKRsa` | secret `roadside-connection-string` → `ROAD_SIDE_PROD` |
| — | RSA MSSQL `apac-staging` (SIT/UAT/preprod, **stopped nightly ~20:00 Bangkok**) | `BKKRsaStaging` (UAT), `BKKRsaPreprodLite` | secret `roadside-connection-string` (UAT entry: `apacadmin`) |

Clients: `/opt/homebrew/opt/mysql-client/bin/mysql`, `sqlcmd` (Homebrew), or Python `pymysql` (the agent reads the
secret into memory and never writes a password to disk or to the conversation).

Rules: prod is read-only and aggregate-first; SIT/UAT writes only through the application or a reviewed script;
never copy customer rows between environments without the developer running it.

## Secrets Manager / SSM names you will need

| Name | Holds |
|---|---|
| `benefit-connection-string-preprod` | Benefit MySQL connection strings for UAT, PREPROD and PROD (keys above) |
| `roadside-connection-string` | RSA MSSQL connection strings per env |
| `/abe/codepipeline/apac-benefit-client-backend-{sit,uat,prod,preprod}/APPSETTINGS_JSON` | ClientService.API settings incl. DB and the frontend-config SSM name |
| `/abe/codepipeline/apac-benefit-frontend-{sit,uat,prod}/APPSETTINGS_JSON` | ABF runtime config (SiteLoungePass, SiteLimo, Okta, feature flags) — served live by the API, no redeploy needed |
| `/abe/codepipeline/apac-benefit-vendor-backend-{sit,prod}/APPSETTINGS_JSON` | ABVB settings incl. Kontent.ai management key |
| `/abe/codepipeline/apac-benefit-sync-data-roadside-{sit,uat,prod,preprod}/APPSETTINGS_JSON` | RSA webhook Lambda settings |
| `roadside/webconfig/{sit,uat}-{roadside,partner}` | RoadSide IIS `Web.config` snapshots (binary) |
| `Benefit-DataProcesser-Client-KTC-UAT-Key-*`, SMC UAT key pair | PGP keys for the data-processor test-drop tool |

## Kontent.ai (CMS)

| Env | Environment id | Used by |
|---|---|---|
| prod | `994226e6-d1a5-023e-0fc9-21571d884f47` | prod **and pre-prod** (RoadSide `BrandCmsService` defaults to prod when `KontentEnvironmentId` is absent) |
| SIT/UAT | `225b0999-fce9-02b4-c44b-ed6990faeeaa` | SIT + UAT share it |

Delivery API is public (`https://deliver.kontent.ai/<env>/items?…`); Management API key in the ABVB SSM entries.

## Mail (data processors)

SES active rule set `benefit-receipt-ruleset-sit` (holds prod, preprod and uat rules). Recipient
`{client}-{env}-import@aspirelifestylesasia.com` → `s3://benefit-raw-email-receiving/{env}/EMAIL/{Folder}/`.
Missing rule = sender gets "550 mailbox not available".

## Atlassian

- Jira/Confluence MCP `atlassian-isos` (OAuth, your ISOS account): reads + Jira comments. Confluence writes are
  blocked on this tenant → `twg` CLI (OAuth on first run). Page attachments (diagram images) → REST with a
  personal API token stored at `~/.config/atlassian/token` (mode 600), basic auth `email:token`,
  header `X-Atlassian-Token: nocheck`.
- Bitbucket: HTTPS with your app password in the git credential helper; agent shells normally cannot push.

## Servers (RoadSide)

UAT/preprod IIS = EC2 `AspireAPAC_Staging` (`i-0c0b0ffcdfec95d6f`), Windows 2019, reachable with
`aws ssm send-command` (no RDP). Sites under `C:\roadside-*.aspireasia.net`. CodePipeline
`roadside-backend-{sit,uat,preprod,production}`; Windows CodeBuild lives in `us-east-1`.
DNS for `aspireasia.net` is in Cloudflare (the Route 53 zone is a stale copy).
