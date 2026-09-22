# OmnicasaAS workspace — APAC Aspire Digital (International SOS)

This folder holds the Aspire Benefit / RoadSide repositories side by side. Read this file first; then the
repo's own `CLAUDE.md`; then the memory notes (loaded automatically — `MEMORY.md` is the index). The kit that
installs all of this is `ai-workspace/` (README there). **Anything non-obvious you learn goes into memory and
is committed to `ai-workspace/memory/` at the end of the ticket.**

## Repositories (local name = Bitbucket repo under `internationalsos/`)

| Local folder | Bitbucket repo | What | Stack |
|---|---|---|---|
| `ABMB` | `apac-booking-modernization-backend` | **RSA / RoadSide** web app (`RoadSide/bkkrsa2020-master/BkkIsos47.sln`): agent portal (MSU), provider portal, partner APIs, Benefit webhooks | .NET Framework 4.8 ASP.NET on IIS (EC2), MSSQL |
| `ABVB` | `apac-benefit-vendor-backend` | **Vendor** backend: vendors, Kontent.ai CMS modules, dealer/provider sync to RSA (`VendorServerless`) | .NET Lambda |
| `ABF` | `apac-benefits-frontend` | **Benefit admin UI** (Blazor WASM, MudBlazor): customers, privileges, reports, vendor module, Data Processor Report | .NET Blazor |
| `ABCB` | `apac-benefit-client-backend` | checkout on the **data-processor** branches: `DataProcesser/` (client customer-file imports, AWS Batch) | .NET 8 console → Docker → Batch |
| `ABCB.Clone` | `apac-benefit-client-backend` | same repo on **`develop`**: `ClientService.API` (Lambda `api/clients/*` — privileges, reports, customers, handback), `WebHookSyncDataRsaBenefit` (`api/webhook-roadside/*`) | .NET Lambda |
| `ai-workspace` | (this kit) | instructions, commands, memory, access recipes, Confluence generators | — |
| `issues/` | — | one task file per ticket (`issues/ABE-xxxx.md`): brief → analysis → implementation → verification → release. Not committed to product repos | — |

The same repo (`apac-benefit-client-backend`) deploys **two different things from different branches** — see the ABCB `CLAUDE.md`.

## Branch → environment (verified from CodePipeline source stages, 21 Sep 2026)

| Repo | SIT | UAT | PROD | Deploy trigger |
|---|---|---|---|---|
| ABCB `ClientService.API` | `develop` → `apac-benefit-client-backend-sit` | `staging` → `…-uat` | `main` → `…-prod` | push to branch |
| ABCB `WebHookSyncDataRsaBenefit` | `roadside-sync-data-sit` | `roadside-sync-data-uat` | `roadside-sync-data-prod` | push to branch |
| ABCB `DataProcesser` | — | `data-processer-pre-production` (UAT job defs) | `data-processer-production` | manual: image push + Batch job-def revision (+ rule repoint) |
| ABVB | `develop` | `staging` | `main` | push / tag |
| ABF | `develop` | `staging` | `main` | push / tag |
| ABMB RoadSide | `roadside_release_sit` (underscores) | `roadside-release-uat` | `roadside-release-production` | push (SIT/UAT); PROD = tag `prod/YYYYMMDD_NN` + manual approval |

**Feature branches: `jira/ABE-xxxx-short-slug`, cut from the branch that feeds the first test environment
(`develop` for ABCB API / ABVB / ABF) — never from `main`.** PR → that branch; QA tests on SIT; promote.

## Environments and data

| Env | Benefit MySQL (Aurora) | RSA MSSQL | Notes |
|---|---|---|---|
| SIT | `Aspire` on cluster `benefit-sit` (tunnel **3375**, admin login from secret `benefit-connection-string-preprod`; app login in SSM `/abe/codepipeline/apac-benefit-client-backend-sit/APPSETTINGS_JSON`) | `BKKRsaStaging` on `apac-staging` | ABF SIT = `api-benefit-sit.aspireasia.net`; SIT and UAT are **different databases** |
| UAT | `AspireProdBackup` on the same `benefit-sit` cluster (tunnel 3375, key `connectionStringBenefitUat`) — yes, despite the name | same server | ABF UAT = `api-benefit-uat.aspireasia.net`; the Data Processor Report is visible only on **benefit-uat** |
| PREPROD | `BenefitPreProdV3` / cluster `preprod-20270707` — **usually STOPPED** | `BKKRsaPreprodLite` | do not test here unless you start the cluster |
| PROD | `Aspire` on `benefit-prod` (tunnel **3382**, `connectionStringBenefitProduction`) — **SELECT only, aggregates over row dumps** | `BKKRsa` on `rsa-prod` (direct, tunnel **3383**; creds secret `roadside-connection-string`) | never write; never paste customer rows into a conversation |

Kontent.ai (CMS): prod env `994226e6-…` (pre-prod shares it — writing "pre-prod" writes prod), SIT/UAT env
`225b0999-…`. Keys in SSM `/abe/codepipeline/apac-benefit-vendor-backend-{prod,sit}/APPSETTINGS_JSON`.
AWS: account `739075353953`, region `ap-southeast-1` (Windows CodeBuild for RoadSide is in `us-east-1`).
Full recipes: `ai-workspace/access/ACCESS.md`.

## How we work (the AI workflow — Confluence "AI in the Development Workflow")

1. `/task-fetch ABE-xxxx` → `issues/ABE-xxxx.md`. Fetch only. The human reviews the file.
2. `/task-analyse issues/ABE-xxxx.md` → read-only: code touchpoints with `file:line`, facts measured on UAT/PROD
   (tag `[measured]`/`[assumption]`), root cause or design, blast radius, questions for BA/QA, plan.
   **Always `SHOW CREATE PROCEDURE` / diff live objects across SIT, UAT and PROD before editing a stored
   procedure — the repo scripts and the three environments drift.**
3. Implement on the feature branch; build; unit tests; one-line commits `ABE-xxxx Imperative summary`, no AI
   trailers; comments say why with the ticket id inline.
4. Verify with evidence: Playwright against SIT/UAT, before/after DB counts, logs. Write it into the task file.
5. Hand-off: Jira comment via the MCP (`addCommentToJiraIssue` works; Confluence writes do not — use `twg`),
   PR description from the task file, release page from the task files of the train.

## What the agent does not do on its own
- No writes to PROD (code, data, config). No `UPDATE`/`INSERT` on SIT/UAT outside the application or a reviewed
  script. No Secrets Manager / IAM / SSM writes. No copying customer rows between environments (PII).
- No `git push` / PR / Jira transition / prod tag without the developer saying so. Pushing usually needs the
  developer's Bitbucket credential anyway — hand them the command.
- For anything refused by the permission classifier: write the exact script, explain it, continue with the rest.

## Conventions and gotchas that bite every time
- IDs are environment-specific (clients, programs, tiers, masterdatas): resolve by code / ProgramNumber /
  MasterCode, never hard-code numbers.
- Excel date cells → `CommonDate.TryParseDateCell`, never `ToString()`. DATETIME strings `dd/MM/yyyy HH:mm:ss`.
- Tier names are plain text or `{"en":"…"}` JSON. Compare through the helper.
- ABF reads its runtime config from SSM via the API, not from the S3 `appsettings.json` (dead).
- Confluence: publish with `twg confluence content create/update … --format html`; diagrams as PNG attachments
  (see `ai-workspace/confluence/`). The Atlassian MCP cannot write Confluence on this tenant.
- Bitbucket pushes from an agent shell fail with `Authentication failed` — expected.

## Where the documentation is
- Confluence AD space → *APAC Aspire Digital Artificial intelligence (AI)* → **AI in the Development Workflow** (overview `6837665931`; parts 1–5; worked examples Sprint 70 `6837895252`, ABE-5461 `6837207394`)
- Confluence AD space → *APAC Aspire Benefit Data Processors* → **Benefit Data Processors** (overview `6837534805`, one page per client) — read the client page before touching a processor; regenerate with `ai-workspace/confluence/data-processors/`
- Repo docs: `ABCB/docs/data-processor/*`, `ABMB/RoadSide/**/docs`, `issues/*-RUNBOOK.md`
