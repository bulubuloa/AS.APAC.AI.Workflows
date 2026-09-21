# apac-benefit-client-backend (ABCB)

One repository, two products, different branches. Check `git branch --show-current` before assuming which one you are in.

## A. `ClientService.API` + `WebHookSyncDataRsaBenefit` — branches `develop` / `staging` / `main`
- `ClientService.API` (Lambda `apac-benefit-client-backend-{sit,uat,prod}`) serves `api/clients/*`: privileges, redemptions, customers, reports (`ReportController` → `ReportService` → MySQL stored procedures), handback runs, parameter store for ABF.
- `WebHookSyncDataRsaBenefit` (Lambda `apac-benefit-sync-data-roadside-*`, branches `roadside-sync-data-{sit,uat,prod}`) serves `api/webhook-roadside/*` for the RSA app. Older schema than the API — no taxonomy rules there except the ABE-4868 live resolver.
- Feature branch from `develop`; PR to `develop` (SIT). Build: `dotnet build ClientService.API/ClientService.API.csproj`.
- Reports are stored procedures: **`SHOW CREATE PROCEDURE` on SIT, UAT and PROD and diff against `database/` before changing one** — they drift (e.g. `Benefit_SP_GenerateDetailedFinanceReport`: repo `database/SPs/Reports/…_sp_2.sql` = UAT; SIT adds `= ''` guards; PROD has different joins/status filter). New scripts go to `database/Sprint<N>/ABE-xxxx_<object>.sql`, idempotent (`DROP … IF EXISTS` + `CREATE`), header with env order, drift notes and rollback file.
- Excel exports: header lists in `Extensions/ImportExportHeader.cs` are ordered and **shared** across exports (`BreakdownFinance.Header` also feeds a legacy privileges export). Add new columns at the end of the order list and insert by position in the mapper; do not renumber.
- Related change to know: ABE-5363 added `customerprograms.ClientCustomerTierId`; `CustomerTypeId` still exists and the SPs still join on it.

## B. `DataProcesser/` — branches `data-processer-pre-production` (UAT) / `data-processer-production`
- .NET 8 console → Docker (`DataProcesser/Dockerfile`, build `--platform linux/amd64`) → AWS Batch (Fargate). `JOBTYPE` selects the client processor (`Constants/JobType.cs`, `Program.cs` switch). 25 client folders under `DataProcesser/Clients/`.
- **Read the client's Confluence page first** (Benefit Data Processors → `<CODE>`): trigger, S3 prefixes, rules, job definitions, image tag, input format, program numbers, gotchas. Facts also in `docs/data-processor/confluence/clients.py`.
- Deploy = push immutable image tag → register job-definition revision → repoint the EventBridge rule if it pins a revision (email clients) → SES rule for a new mailbox. Never `:latest` in prod; never run `MacOS_ECR_Push.sh` without reading it.
- Test on UAT (preprod DB is stopped): QA test-drop Lambda `benefit-dataprocessor-testdrop-uat` (source `DataProcesser/infra/dataprocessor-testdrop/`), or manual `aws batch submit-job` with `CONNECTION_TARGET=UAT`. Verify in ABF → Data Processor Report on **benefit-uat** and in the handback bucket `aspire-dataprocessor-handback-report/{CODE}/UAT/`.
- Conventions: `FieldMapping` key = DTO property name, value = DB FieldCode (new clients keep them identical); `ProgramTierLookup.ByProgramNumber` (never ClientId/ProgramCode); `HandbackBatchProcessorBase` for every processor; read the triggering S3 key (`GetAttachmentsForThisRun`); customer name to core columns **and** JSON; dates via `TryParseDateCell`.
- Queue-row clients (KPI, KUC, SMC, MSC, CSM) read `customer_import_file_template`, not the S3 event: one PENDING_INSERT at a time; the S3 upload itself fires a job.
- Unit tests: `dotnet test DataProcesser/DataProcesser.Tests` (≈630). New client: clone TRI (six files + JobType const + Program.cs case) — checklist on the Data Processors overview page.
- Untracked local files (`msc12.csv`, `issues/`) never enter a release branch.
