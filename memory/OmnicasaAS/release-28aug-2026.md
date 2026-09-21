---
name: release-28aug-2026
description: "28-Aug RSA prod release — ABMB deployed 27 Aug 00:59, what's still pending (ABVB/ABF/ABCB deploys, sweep, hostname mystery)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9d5486f7-6f25-4ff6-a72b-e38c632ec649
  modified: 2026-08-26T18:04:53.376Z
---

**ABMB 27 Aug 00:59 run was a TEST DEPLOY - REVERTED same night** (sites restored from C:\RoadSide-Backup\2026.08.27.*, VC_ConsultType view reverted to legacy def; real deploy planned 28 Aug: re-run MasterData script + new prod/ tag + approve; DB otherwise stays prepared) — tag `prod/20260827_02`, pipeline exec `4e511115`, CodeDeploy `d-0S0JYOGUK`, verified live (logins + dispatcher activity minutes after). Full runbook: `Omnicasa.Mobile.ABMB/docs/RELEASE-28AUG-2026.md` + `DatabaseScript/Release-28Aug-2026/RUN-ORDER.md`; master scripts `20260828_MASTER_PreDeploy.sql` / `_Rollback.sql`. See [[abmb-roadside-cicd]], [[abe-brand-management]].

Done on prod: master DB script (log in session scratchpad; backup suffix 20260821 in `bak` schema — 345,111 consult values), snapshots `rsa-prerelease-20260826` + `-20260827-deploy`, CMS seeds + `porsche_rsa` published in env 994226e6, NIMITMAI dealer bActive=0 (ABE-5322). Consult migration was CANCELLED by ABE-5355 (per-client values via SysLookup CONSULT_TYPE / CONSULT_TYPE_PTH + `VC_ConsultType`; detection by clientCode='PTH').

**Still pending after 27 Aug:**
- ABVB `release/prod/ABE-5319-5320-porsche` (ebf138c) and ABF `release/prod/ABE-5320-porsche` (1c4d289cb) — push + PR + deploy to main. Porsche dealer sync + ABE-5322 prevention are NOT live until ABVB ships; a Porsche vendor saved before that needs a re-save after.
- ABCB `release/prod/data-processor-20260825` — PII decision open (strip `cc1605227`/`2141219b3` data files: ABE-4441 xlsx + preprod dumps) before pushing to `data-processer-production`; separate deploy day; its Benefit-MySQL scripts each need a was-it-already-run check; `ABE-4838` is preprod-only.
- Dealer status sweep beyond NIMITMAI (prod CMS-inactive vs RSA-active list) — get business sign-off first.
- **Mystery**: prod Web.config `BkkRsaEntities` points at `rsa-production.cofpzhamf3ov...` which does NOT resolve and no such RDS instance exists (only `rsa-prod`); app works, so either a hosts-file entry on the prod box or the pasted config is stale. Deploys never touch Web.config. Check before any new server/config restore.
- 5320 script latent bug: references `cloud.Client.bActive` (column exists nowhere) — INSERT branch + AFTER report fail on a fresh-client run (benign when PTH exists; threw 2 harmless Msg 207 on prod).
- Bastion SG `sg-006ea52049f6aee44` got `171.243.48.19/32` added for port 22 (26 Aug session) — the usual rotating-IP pattern.
