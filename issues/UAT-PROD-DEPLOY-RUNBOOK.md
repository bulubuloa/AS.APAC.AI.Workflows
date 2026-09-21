# UAT / PROD deployment runbook

Everything outstanding from the SIT work of 18–21 Aug 2026, in the order it must be done.
Written so nothing depends on remembering this conversation.

**The recurring trap in every section below: some steps must run BEFORE the app deploys, not
after.** Each one is marked.

---

## 0. Read this first — two things already true

**SIT and UAT share one Kontent environment** (`225b0999-fce9-02b4-c44b-ed6990faeeaa`).
Confirmed from both Web.configs. Consequences:

- The ABE-5307 defect seed run on 21 Aug **has already changed UAT's data**. UAT needs no seed.
- **UAT's job screen is showing 34 defects to every client right now** — the seed added 20 Porsche
  defects, and UAT still runs the old code that ignores `client_specific`. This corrects itself the
  moment the ABE-5307 code deploys there. Tell QA before they raise it.
- Any future CMS change for one of them hits the other.

**Production uses a different Kontent environment** (`994226e6-d1a5-023e-0fc9-21571d884f47`) and is
untouched: `defect_issue` still has only `name`, 14 items.

---

## 1. ABE-5307 — Client-Specific Defect Issues

### Branch
`jira/ABE-5307-defect-client-specific-sit` — commit `e8b82392` (4 files)

### UAT

| Step | Action |
|---|---|
| 1 | **Nothing to seed** — shared CMS env, already done |
| 2 | Deploy the code |
| 3 | Verify (below) |

### PROD — seed BEFORE or AFTER the app deploy (either is safe)

Deploy order does not matter here, because the code degrades gracefully: with `client_specific`
absent, every defect reads as blank = global, i.e. exactly today's behaviour. Verified on SIT.

```bash
cd RoadSide/bkkrsa2020-master/BkkRsa/Sql-scripts

ENV_ID=994226e6-d1a5-023e-0fc9-21571d884f47 \
MGMT_KEY='<prod Kontent Management API key>' \
  python3 abe5307_defect_client_seed.py --new-client PTH --existing-client HOT --dry-run
```

Check the dry run reports `stamped=14 created=20`, then re-run without `--dry-run`.

> The prod Management key is **not** the SIT/UAT one — the environments differ. Get it from the
> prod RSA Web.config (`KontentManagementApiKey`) or from a Kontent admin.

### Verify (any environment)

```
GET /msu/clientdefects/380    -> 14   (Honda, HOT)
GET /msu/clientdefects/<porsche clientId>  -> 20   (PTH)
GET /msu/clientdefects/<any other client>  -> 0
```

### Expected, not a bug

Clients other than Honda/Porsche now get an **empty** Defect Issue list. That restores the original
design — the legacy `cloud.UC_DefectIssue` table holds those 14 defects against **clientId 380 only**,
on both SIT and UAT. ABE-4681 accidentally made the list global when it moved to the CMS; this
closes that. Existing jobs keep their stored values.

Clients currently affected (they have jobs with defects and will lose the picker):
- SIT: SMC 5, AEO 4, ONE 2, KAS 1, AME 1, COF 1, AIA 1
- UAT: **MBZ 3**, NAN 3, MIT 2

**MBZ is worth a decision** — Mercedes is a real RSA brand like Honda and Porsche. If Benz should
have its own defect list, that is a follow-up seed, out of scope here.

---

## 2. ABE-5305 — Consult field values

### Branch
`jira/ABE-5305-consult-type-sit` — 5 commits

### ⚠ The SQL MUST run BEFORE the app deploys

`"Breakdown – Technical Defect"` is 28 characters; the column is `nvarchar(20)`. Deploy the app
first and users get an option they cannot save.

```
RoadSide/bkkrsa2020-master/BkkRsa/Sql-scripts/20260818_ABE-5305_ConsultType.sql
```

Run it against each environment's RSA database, then deploy. It is idempotent and prints
before/after. Steps 1 and 7 only report — read their output.

What it does: widens `cloud.JobInfo.consultType` to `nvarchar(50)`, **`sp_refreshview` on
`cloud.VW_JobInfo`**, updates `dbo.SysLookup` master values with `icode` ordering, exposes `icode`
through `cloud.VC_ConsultType`, migrates existing jobs.

> The `sp_refreshview` is not optional. The Job screen, Job Report and Compass Report all read the
> **view**; a non-schemabound view keeps the old 20-char metadata after `ALTER TABLE` and silently
> truncates to `"Breakdown – Technical Def"` everywhere.

### Data waiting

- **UAT**: 79 × `Breakdown`, 1 × `Usage Advisory`
- **PROD**: not checked — run the script's step 1 to see before committing to a window

### Verify

```sql
SELECT consultType, COUNT(*) FROM cloud.JobInfo GROUP BY consultType;   -- no Breakdown / Usage Advisory
SELECT UNICODE(SUBSTRING(ConsultType,11,1)) FROM cloud.VC_ConsultType
 WHERE ConsultType LIKE N'Breakdown%';                                   -- expect 8211 (en dash), not 63 '?'
```

Then in the UI: the dropdown must read blank → Accident → Breakdown – Technical Defect → Others, and
saving the 28-character value must succeed.

---

## 3. Porsche client code — `PTH` alignment

Production has always used **`PTH`** (Benefit client Id 115, `NameEN = "AAS Auto Service Co.,Ltd."`,
`DescriptionEN = "Porsche RSA"`). SIT briefly used `POR` and has been corrected.

**"Porsche RSA" is the vendor group name and the client's *description* — not the client name.**
RSA takes `clientName` from Benefit's `NameEN`.

### Already done
- ABVB `VendorConstants` → `[PorscheGroupCodename] = "PTH"` — merged to `develop` (PR #941), **deployed to SIT**
- Benefit SIT client 402 aligned; 1 customer + 3 privileges moved off `POR`
- RSA SIT `cloud.Client` 2209 → `PTH` / `AAS Auto Service Co.,Ltd.`

### UAT / PROD

| | Benefit | RSA `cloud.Client` |
|---|---|---|
| UAT | **no Porsche client at all** | **none** |
| PROD | `PTH` exists (Id 115) | not checked |

So for UAT: create the Porsche client as **`PTH`**, `NameEN = "AAS Auto Service Co.,Ltd."`. It will
sync to RSA. Do **not** use `POR`.

⚠ **Promote the ABVB change before creating any Porsche dealer**, or the sync resolves a client code
that does not exist and silently skips the dealer (the G1 guard logs and returns).

### Leftover on Benefit SIT (not done — sandbox blocked me)

Client row 678 still holds `ClientCode='POR'` and owns the Porsche program/tier records:

```sql
UPDATE client_customer_tiers SET ClientId=402 WHERE ClientId=678;
UPDATE clientprograms        SET ClientId=402 WHERE ClientId=678;
UPDATE programs              SET ClientId=402 WHERE ClientId=678;
UPDATE clients SET ClientCode='PORX', NameEN='[deprecated] merged into PTH 402'
 WHERE Id=678 AND ClientCode='POR';
```

---

## 4. ABE-5319 / ABE-5329 — Porsche display + provider search

### Branch
`jira/ABE-5320-porsche-dealer-sync-sit` — 1 unpushed commit (`a474fe61`, the reusable test suite).
The functional fixes are already merged and deployed to SIT.

Nothing environment-specific. Standard promotion.

### Known data prerequisite

A Porsche provider will not appear on the Job Map until its truck is **registered in the provider
app and reporting GPS** — `GetSql_LoadProvider` requires `tokenSerial`, `lat`, `lng`, `active=1`,
`istatus=READY` and a matching `VehService` row. A newly synced truck is `NOTREGIS` and invisible.

Also: the Truck List's **"Only Registered" filter is ticked by default**, so newly synced trucks look
missing. This has been mistaken for a bug twice.

---

## 5. Production CI/CD

### Branch
`roadside-cicd-production` — 3 commits, **must be merged into `roadside-release-production`**

All four AWS resources exist already:

| Resource | Value |
|---|---|
| EC2 tag | `DeployProd=roadside-prod` on `i-03c403d112b5db4b1` |
| CodeDeploy group | `roadside-backend-production` (app `roadside-backend`) |
| CodeBuild (us-east-1) | `roadside-backend-production` |
| CodePipeline | `roadside-backend-production` — V2, QUEUED |

**Zero deployments have reached production.** The pipeline's one run failed at Build with
`YAML file does not exist`, because the prod branch has no `buildspec.yml` yet — that is what the
branch above supplies.

### Release process — tag, not branch

```bash
git push origin roadside-release-production     # merging deploys NOTHING
git tag prod/20260821_01
git push origin prod/20260821_01                # this starts the pipeline
```

Then it **waits at `Approve`** until a human approves. Stages: `Source → Build → Approve → Deploy`.

This differs deliberately from SIT/UAT, which deploy on branch push. Tell the team.

Sites deployed: `BkkRsa → C:\RoadsideWebAdminProduction`, `BkkRsaPartner → C:\RoadSideWebPartnerProduction`.
**RoadSideWebCompass is intentionally excluded** — `BkkRsaCompass` is not in the build bundle.

Backups land in `C:\RoadSide-Backup\<timestamp>` before each sync. The first prod deploy has never
been exercised — do it at a quiet hour and confirm the backup folder appears before approving.

---

## 6. Infrastructure — open risks

### ⚠ The TLS outage will recur

On 20 Aug the staging box (`i-0c0b0ffcdfec95d6f`) lost all TLS in both directions for ~14 hours.

**Root cause:** local Group Policy *SSL Cipher Suite Order* contained OpenSSL-format cipher names
(`ECDHE-RSA-AES256-GCM-SHA384`) instead of Windows IANA names (`TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384`),
and the string exceeded the 1023-character limit. Schannel discarded the list, leaving
**one usable cipher suite** — so every handshake failed with event **36874**.

It broke inbound IIS, outbound API calls (`manage.kontent.ai`) and the SSM agent's own workers
simultaneously.

**It is not fixed.** After `gpupdate /force`, the registry key returned:

```powershell
Test-Path 'HKLM:\SOFTWARE\Policies\Microsoft\Cryptography\Configuration\SSL\00010002'   # True
```

Until someone sets **gpedit.msc → Computer Configuration → Administrative Templates → Network →
SSL Configuration Settings → SSL Cipher Suite Order** to **Not Configured**, the next policy refresh
can take the box down again. Verify with `(Get-TlsCipherSuite).Count` — healthy is ~30–40, broken is 1.

If the list must exist, it has to use `TLS_*` names only, stay under 1023 characters, and **drop the
`NULL` suites** (`TLS_RSA_WITH_NULL_SHA256`, `TLS_RSA_WITH_NULL_SHA`) which provide no encryption.

### Credentials to rotate

Exposed during the incident and should be cycled: the server **Administrator password**, and the
**Kontent Management API key** for env `225b0999` (valid until 2028, full write access).

### Latent bug — duplicate client codes

`cloud.Client.clientCode` has **no unique index**, and the dealer sync resolves it with
`FirstOrDefault` and no ordering, in three places in `ProviderSyncBenefitController`. Duplicates
exist today: 12 codes on SIT, 6 on UAT (e.g. `KAS` → 323 *and* 1974). A dealer can attach to the
wrong client non-deterministically. Same failure mode as ABE-5322. Worth its own ticket.

### Minor

Typing text into the Dealer list's **Dealer ID** field returns `Incorrect syntax near '25'` — the
value is concatenated into SQL unescaped.

---

## 7. Deployment order — the short version

1. **ABE-5305 SQL** on the target RSA database ← before its app deploy
2. Create the Porsche client as **`PTH`** where missing (UAT)
3. Promote **ABVB** (`PTH` constant) before any Porsche dealer sync
4. Deploy the RSA app branches
5. **ABE-5307 seed** on prod's Kontent env only (UAT already done via the shared env)
6. Verify each section above
7. Production: merge to `roadside-release-production`, then push a `prod/YYYYMMDD_NN` tag and approve
