# UAT / PROD release — branches, migrations, CMS

Prepared 21 Aug 2026 · **updated 25 Aug 2026** (§0 below supersedes the branch lists for the PROD
release; the rest of the document remains the UAT reference).

---

## 0. PROD release — 28 Aug 2026 (reviewed 25 Aug)

### 0.1 The four branches

| Repo | Branch → target | Content | State |
|---|---|---|---|
| **ABMB** | `release/prod/release-28Aug2026` → `roadside-release-production` | 19 commits: full 28-Aug feature set (Brand Mgmt, Porsche RSA, Consult, Defect-per-client, ABE-5328/5333) **plus the 25 Aug fixes** ABE-5341/5342/5343/5344/5345/5346/5350/5352 | local is **2 commits ahead of origin** (`6e716366` dealer-endpoint fix, `6773b369` doc update) — push before tagging |
| **ABVB** | `release/prod/ABE-5319-5320-porsche` → `main` | **1 squashed commit** `ebf138c` (brand groups for every RSA brand, dealer active-status sync = the ABE-5322 fix, PTH client code, Ver2 group+note) — cut fresh off pulled `main`, so it already reflects the CountryCode hotfix | not pushed |
| **ABF** | `release/prod/ABE-5320-porsche` → `main` | **1 squashed commit** `1c4d289cb` (vendor group keyed on ClientCode, vendor_external_id cleanup) — cut off `origin/main`; only the 4 ABE-5320 commits, none of the 31 unreleased staging commits leaked in | not pushed |
| **ABCB** | `release/prod/data-processor-20260825` → `data-processer-production` | 43 commits: everything since prod's Jul-17 tip (MSIG/MSC processor, FWD/SOR/HOT/HOG/MBZ report + ProgramNumber work, handback-concurrency fixes, security fix) **minus UOB-pbc** (both ABE-5223 commits reverted + dangling `AspireContext` mappings removed, verified no dangling refs) | not pushed — **see ⚠ below before pushing** |

**⚠ ABCB data-file warning (decide before pushing):** two housekeeping commits drag non-code
content into production history — `cc1605227` includes `issues/ABE-4441/*.xlsx` (real FWD client
files from an investigation — possible customer PII) and `2141219b3` includes
`LocalTests/handback-detail-dump/*` (preprod run dumps) and `.codex/config.toml`. Recommendation:
strip those two commits (or at least the data files) from the release branch before it reaches the
production branch.

**Ship-together rule:** ABF + ABVB + ABMB are one feature (Porsche RSA / dealer sync) — deploy
ABVB before any dealer sync fires, and don't leave ABMB behind or the ABE-5350 dealer overlay and
ABE-5322 status sync stay half-wired. ABCB is independent.

### 0.2 Steps that need NO source deploy — can run today

| Step | Where | Note |
|---|---|---|
| Create + publish `porsche_rsa` ("Porsche RSA") in `vendor_group_list` | Kontent PROD `994226e6` | **pending BA sign-off on the codename**; without it no Porsche dealer can ever be created or synced |
| `abe4681_cms_seed.py` + `abe5307_defect_client_seed.py` (dry-run first) | Kontent PROD | needs the prod Management key (SIT/UAT key does not work) |
| RDS snapshot + `20260821_PreDeploy_Backup.sql` | RSA PROD DB | **snapshot `rsa-prerelease-20260826` taken 26 Aug, available** ✔ (7-day PITR also active) |
| `20260723_ABE-4681_…`, `20260818_ABE-5305_…` (widen only), `20260826_ABE-ConsultType_MasterData.sql`, `20260825_ABE-5341_Brand255…`, `20260821_ABE-5320_PorscheClient.sql` | RSA PROD DB | all additive/widening — safe ahead of the deploy; order per `RUN-ORDER.md`. **The 344k-row consult migration is CANCELLED by ABE-5355** (script now says DO NOT RUN — legacy jobs keep Breakdown/Usage Advisory; only PTH uses the new values) |
| **ABE-5322 data repair**: `UPDATE cloud.ClientDealer SET bActive=0 WHERE vendorCmsId='fea2b729-53df-4e07-b32f-18594be33c95'` (NIMITMAI) + sweep all dealers CMS-inactive but RSA-active | RSA PROD DB | fixes the visible symptom immediately; the ABVB code fix only prevents recurrence on the *next* vendor save |
| Verify `KontentManagementApiKey` present in prod `Web.config` | prod RSA server | absent ⇒ Brand Management save fails silently |
| ABCB DB scripts riding the branch: `ABE-4765.sql`, `Sprint63/ABE-4833-MAZ_Coverage_Fix.sql`, `ABE-4836-MAZ_ProgramDates_Backfill.sql`, `ABE-4858-dispatch-validation-indexes.sql`, report SPs | Benefit PROD MySQL | read each header first — `ABE-4838-MSU_Preprod_Fix.sql` is **preprod-only**, do not run on prod |
| MSC (MSIG) SFTP bridge Lambda | AWS infra | `DataProcesser/infra/msc-sftp-bridge/` — the MSC processor receives nothing until this Lambda + SFTP wiring exists in prod |

### 0.3 Deploy order

```
1. Push the four branches, raise PRs (ABVB→main, ABF→main, ABCB→data-processer-production,
   ABMB merge → roadside-release-production)
2. Run every §0.2 step that is not yet done (all are deploy-independent)
3. Deploy ABF → ABVB → ABMB   (ABMB: tag prod/20260828_NN after the merge — merge alone deploys nothing)
4. Deploy ABCB data processor
5. Verify (§6) + re-save one Porsche vendor in ABF and watch cloud.ClientDealer follow it
```

### 0.4 Post-deploy verification added 25 Aug

- Dealer edit page in RSA shows CMS fax/dealer code (first time ever — watch `wlib.EventLog` for
  `DealerDetailCMS` errors; 401s mean the ABE-5345/5346 token fix isn't live).
- Benefit redeem → RSA job (mode M) → hand-typed unknown provider name → save must error
  ("The provider X is invalid for the privilege benefit…").
- Brand create with a 255-char name saves; a brand/model used by a job shows no Delete button.
- Deactivate a vendor in ABF prod → its RSA dealer goes `bActive=0` (ABE-5322).

---

---

## 1. Deployment topology

Know which branch each environment builds — the three repos do **not** use the same names.

| Repo | Pipeline | SIT | UAT | PROD |
|---|---|---|---|---|
| **ABMB** RoadSide backend | `roadside-backend-*` | `roadside_release_sit` | `roadside-release-uat` | `roadside-release-production` |
| **ABVB** vendor backend | `apac-benefit-vendor-backend-*` | `develop` | `staging` | `main` |
| **ABVB** sync-data-roadside | `apac-benefit-sync-data-roadside-*` | — | `roadside-sync-data-uat` | `roadside-sync-data-prod` |
| **ABF** benefit frontend | `apac-benefit-frontend-*` | `develop` | `staging` | `main` |

SIT and UAT deploy on **branch push**. Production deploys **only on a tag** `prod/YYYYMMDD_NN`
and then waits for manual approval.

---

## 2. The branches

### Porsche RSA — ABE-5319, ABE-5320 (+ ABE-5329)

| Repo | Branch | Commits |
|---|---|---|
| ABMB | `release/uat/ABE-5319-5320-porsche` | 17 |
| ABVB | `release/uat/ABE-5319-5320-porsche` | 7 |
| ABF | `release/uat/ABE-5320-porsche` | 4 |

**All three must ship together.** ABF writes the vendor group, ABVB syncs it to RSA keyed on
client code, ABMB displays it. Any one alone leaves the feature half-wired.

Includes `20260821_ABE-5320_PorscheClient.sql` and `README-CMS.md`.

### Defect Issue per client — ABE-5307

| Repo | Branch | Commits |
|---|---|---|
| ABMB | `release/uat/ABE-5307-defect-issue` | 1 |

### Consult field — ABE-5305

| Repo | Branch | Commits |
|---|---|---|
| ABMB | `release/uat/ABE-5305-consult-type` | 5 |

### Vendor CMS module selection — ABE-5328

| Repo | Branch | Commits |
|---|---|---|
| ABMB | `release/uat/ABE-5328-vendor-cms-module` | 1 |

### Vehicle brand & engine — ABE-4681/5238, ABE-4796/5165, ABE-4797/5164, ABE-4798, ABE-5310

**Already merged into UAT — no branch needed.** Verified: `cloud.JobInfo` brand/engine fields, the
models and the dropdown behaviour are all present on `roadside-release-uat`. What remains is the
**production** promotion, which has never happened — see §5.

---

## 3. Merge order into UAT

Two files are touched by more than one feature, so order is not free:

```
RoadSide/.../Views/Report/JobInfo-Html.cshtml   ABE-5305 (ConsultType) + ABE-5320 (Dealer Code/Name)
RoadSide/.../Views/Msu/Job.cshtml               ABE-5307 (defects) + ABE-5310 (vehicle fields)
```

Each branch applies **cleanly to UAT on its own**. Merging the second one will need a small manual
resolution in the file above — keep **both** feature's columns and set the "No data found"
`colspan` to the new total.

Recommended order, largest first so the conflicts land once:

```
1. release/uat/ABE-5319-5320-porsche      (ABMB + ABVB + ABF together)
2. release/uat/ABE-5305-consult-type      -> expect the JobInfo-Html.cshtml resolution here
3. release/uat/ABE-5307-defect-issue
4. release/uat/ABE-5328-vendor-cms-module
```

---

## 3a. Backup — before ANY migration

Both scripts live on the **Porsche** branch, which merges first, so they are available from the
start of the release.

```bash
# 1. RDS snapshot - the only thing that protects against a mistake outside the tracked objects.
#    RDS does not allow native BACKUP DATABASE.
aws rds create-db-snapshot --region ap-southeast-1 \
    --db-instance-identifier <instance> --db-snapshot-identifier rsa-prerelease-20260821
aws rds wait db-snapshot-available --region ap-southeast-1 \
    --db-snapshot-identifier rsa-prerelease-20260821
```

```
# 2. targeted backup into schema `bak` - jobs, dropdown values, clients, view definitions,
#    column shapes. Refuses to run twice over the same suffix.
20260821_PreDeploy_Backup.sql
```

Rollback is `20260821_PreDeploy_Rollback.sql`. Read its header first — it restores **data and
views** but deliberately does not drop the new columns or narrow `consultType`, because both
destroy data captured since the deploy. Roll the **application** back before the data, or the new
code meets the old schema.

If the release has been live long enough for real data to accumulate, restore the snapshot to a
*new* instance and copy rows across rather than rolling back in place.

---

## 4. Migrations — UAT

Run in this order. **Steps marked ⚠ must precede the app deploy.**

| # | What | Where | Notes |
|---|---|---|---|
| **0** ⚠ | **RDS snapshot**, then `20260821_PreDeploy_Backup.sql` | RSA UAT DB | **run before anything else**; refuses to overwrite an existing backup |
| 1 ⚠ | `20260818_ABE-5305_ConsultType.sql` | RSA UAT DB | 28-char value vs `nvarchar(20)`; **79 `Breakdown` + 1 `Usage Advisory`** waiting |
| 2 ⚠ | `20260821_ABE-5320_PorscheClient.sql` | RSA UAT DB | creates client `PTH`; UAT has **no** Porsche client today |
| 3 | Benefit UAT: create the Porsche client | Benefit UAT (`AspireProdBackup`) | `ClientCode='PTH'`, `NameEN='AAS Auto Service Co.,Ltd.'`, `DescriptionEN='Porsche RSA'`. **Verified 21 Aug: UAT has neither PTH nor POR** |
| 4 | ABE-5307 CMS seed | — | **already done.** SIT and UAT share Kontent env `225b0999` |
| 5 | Deploy ABF → ABVB → ABMB | | ABVB before any Porsche dealer sync |

> **On the Benefit environments.** `connectionStringBenefitUat` and `connectionStringBenefitSit`
> point at the **same server** (`benefit-sit.cluster-…`) and differ only by database — SIT is
> `Aspire`, UAT is `AspireProdBackup`. Despite its name that database is *not* a current copy of
> production: prod holds 90 clients, UAT 297. Verified by connecting and reading
> `SELECT DATABASE(), @@hostname` on each.
>
> **The client code is `PTH` everywhere. `POR` was a mistake and no longer exists.** Benefit SIT was
> consolidated on 21 Aug: client 678 is `PTH` / *AAS Auto Service Co.,Ltd.* and holds every
> dependent; the old `POR` row (402) is retired as `PORX`. Production has always been `PTH`
> (client 115). Never create a `POR` client.

> **UAT is in a temporary odd state right now.** The ABE-5307 seed ran against the shared Kontent
> environment on 21 Aug, so UAT already holds 34 defects while still running the old global
> endpoint — every client currently sees all 34. Deploying ABE-5307 corrects it. Tell QA before
> they raise it as a bug.

## 5. Migrations — PRODUCTION

Production is further behind than UAT: **the vehicle-brand DDL has never run there.**
`roadside-release-production` carries only the two 2025 scripts.

Verified directly against the production database on 21 Aug 2026:

| # | What | Where | Notes |
|---|---|---|---|
| **0** ⚠ | **RDS snapshot**, wait for `available`, then `20260821_PreDeploy_Backup.sql` | RSA PROD DB | **mandatory** — the migration rewrites 344k rows and ALTERs a live table |
| 1 ⚠ | `20260723_ABE-4681_AddBrandEngineSystem_JobInfo.sql` | RSA PROD DB | **CONFIRMED MISSING** — `brand` and `engineSystem` do not exist on prod |
| 2 ⚠ | `20260818_ABE-5305_ConsultType.sql` **steps 1-5 and 7 only** | RSA PROD DB | **CONFIRMED NEEDED** — `consultType` and `VW_JobInfo` are both still `nvarchar(20)` |
| 2b | ~~`20260821_ABE-5305_ConsultType_MigrateBatched.sql`~~ **CANCELLED by ABE-5355 (26 Aug)** | — | do NOT migrate: legacy jobs keep Breakdown / Usage Advisory; only PTH jobs use the new values via `CONSULT_TYPE_PTH`. Run `20260826_ABE-ConsultType_MasterData.sql` instead (see §0.2) |
| 3 | `20260821_ABE-5320_PorscheClient.sql` | RSA PROD DB | **already satisfied** — prod has `clientId 1962` = `PTH` / *AAS Auto Service Co.,Ltd.* Run it anyway; it is a no-op that reports duplicate codes |
| 4 | `abe5307_defect_client_seed.py` | Kontent **prod** `994226e6…` | prod has the 14 defects but **no `client_specific` element**; needs the prod Management key |
| 5 | Confirm `KontentManagementApiKey` in prod `Web.config` | prod RSA | absent ⇒ Brand Management fails; read paths still work and hide it |
| 6 | Deploy, then tag `prod/YYYYMMDD_NN` and approve | | branch merge alone deploys nothing |

Prod Kontent already has `vehicle_brand` (47), `vehicle_model` (398), `engine_system` (4),
`defect_issue` (14) — so only the `client_specific` element and the 20 PTH defects are missing.

Full CMS procedure: `RoadSide/bkkrsa2020-master/BkkRsa/Sql-scripts/README-CMS.md`.

---

## 6. Verification

```bash
# ABE-5305
npx playwright test tests/consult-type.spec.ts        # 13 specs, all green on SIT
# ABE-5319
npx playwright test tests/abe-5319-provider.spec.ts   # 12 specs
```

```
# ABE-5307 - via an authenticated session
/msu/clientdefects/380    -> 14   (Honda HOT)
/msu/clientdefects/<PTH>  -> 20   (Porsche)
/msu/clientdefects/<any>  ->  0
```

Expected and **not** a bug: clients other than Honda/Porsche now get an empty Defect Issue list.
That restores the pre-ABE-4681 design — the legacy `cloud.UC_DefectIssue` holds those 14 defects
against `clientId 380` only. Existing jobs keep their stored values.

Clients that will notice: **UAT** MBZ 3 jobs, NAN 3, MIT 2 · **SIT** SMC 5, AEO 4, ONE 2, KAS 1,
AME 1, COF 1, AIA 1.

---

## 7. Known issues to carry forward

- **Duplicate `clientCode`** — no unique index on `cloud.Client.clientCode`; the dealer sync uses
  `FirstOrDefault` with no ordering in three places. 12 duplicate codes on SIT, 6 on UAT. A dealer
  can attach to the wrong client non-deterministically. Step 4 of the Porsche script reports them.
- **Dealer list SQL injection** — text in the Dealer ID field returns `Incorrect syntax near '25'`;
  the value is concatenated unescaped.
- **TLS / Group Policy on the SIT+UAT host** — local policy *SSL Cipher Suite Order* contains
  OpenSSL-format cipher names and exceeds the 1023-char limit, collapsing Schannel to one cipher
  suite and killing all TLS in both directions. Fixed by reboot on 21 Aug, but the policy is
  **still set to re-apply** — `gpedit.msc` → Computer Configuration → Administrative Templates →
  Network → SSL Configuration Settings → set to *Not Configured*, or it recurs.
- **Mobile Vendor checkbox (ABE-5328)** — the RSA half is fixed on its branch. The reported
  "auto-checks in edit mode" symptom is in the **Benefit vendor form**, not RSA, and is unfixed.
- **MBZ defects** — Mercedes has jobs using Defect Issue but no list of its own. Out of scope here.
