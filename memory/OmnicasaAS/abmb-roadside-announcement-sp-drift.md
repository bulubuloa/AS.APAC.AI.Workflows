---
name: abmb-roadside-announcement-sp-drift
description: RoadSide SP drift — ABE-4470 script clobbers ABE-4468 SPs; fixed on prod 2026-07-10 and UAT 2026-09-18; repo script now guarded
metadata: 
  node_type: memory
  type: project
  originSessionId: 25378bc3-1c5e-4bfd-952e-3ac16d2a4e89
  modified: 2026-09-18T04:28:51.032Z
---

ABMB RoadSide (`Omnicasa.Mobile.ABMB/RoadSide/bkkrsa2020-master`): `Scripts/ABE-4470_ApprovalWorkflow_Apply.sql` holds OLD 9-param `sp_InsertAnnouncement`/`sp_UpdateAnnouncement` (no `@EffectiveDate`), while `ABE-4468_ValidityPeriod_Apply.sql` has the current 10-param versions matching the code. Running 4470 after 4468 (ticket order) clobbers the SPs → "too many arguments" on announcement create/edit.
- Prod (`rsa-prod...rds`, DB `BKKRsa`): broke in 2026-06-30 release, fixed 2026-07-10 by recreating SPs from 4468.
- UAT (`apac-staging...rds`, DB `BKKRsaStaging`, creds = `roadside/webconfig/uat-roadside` secret → `BkkRsaConString`, user apacadmin): clobbered 2026-07-08, fixed 2026-09-18 by re-running the full 4468 script (idempotent). Auto mode blocks DB writes — user must run via `! python3 apply4468.py` in scratchpad.
- **Script chain order matters**: 4470_ApprovalWorkflow → 4468_ValidityPeriod → 4470_MobileVisibilityTimezone (adds `@NowLocal` to sp_GetActiveAnnouncements + sp_GetActiveAnnouncementById; mobile list breaks silently/empty without it) → 4470_HardDelete. Re-running 4468 alone clobbers the mobile SP — always follow it with MobileVisibilityTimezone (done on UAT 2026-09-18). Generic runner: scratchpad `runsql.py <file.sql>` (needs `db.py` built from the uat-roadside Web.config secret).
- Repo fix 2026-09-18 (branch `roadside-release-uat`, uncommitted at time of writing): 4470 script sections 3.1–3.5 and 3.9 wrapped in `SET NOEXEC ON/OFF` guarded by `COL_LENGTH(EffectiveDate)`, so it no longer clobbers 4468 SPs. Check SIT/preprod DBs if the same error shows there.
Related: [[abmb-roadside-cicd]]
