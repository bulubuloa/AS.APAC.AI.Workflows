# Memory Index

- [ABE repo aliases & CMS dynamic modules](abe-repo-aliases-and-cms-modules.md) — ABVB/ABF repo mapping, ABE-4325 rework branches, module touchpoint checklist, DB typo gotcha
- [ABF frontend runtime config flow](abf-frontend-runtime-config-flow.md) — where SiteLoungePass/SiteLimo etc. actually live (SSM param via get-parameter-store), S3 appsettings.json is dead
- [ABMB RoadSide CI/CD](abmb-roadside-cicd.md) — roadside-backend-uat pipeline, Windows CodeBuild only via us-east-1, AspireAPAC_Staging server paths & SSM access
- [ABMB RoadSide announcement SP drift](abmb-roadside-announcement-sp-drift.md) — ABE-4470 script clobbers 4468 SPs (@EffectiveDate); prod fixed 2026-07-10, UAT fixed 2026-09-18, repo script now guarded
- [ABE-4681 Job vehicle fields](abe-4681-vehicle-fields.md) — Brand/Model/Engine System/Defect Issue on RSA jobs; CMS types created (defect seed pending), readonly-gating gotcha, deploy steps
- [ABMB Kontent env switch](abmb-kontent-env-switch.md) — UAT now on env 225b0999; the 4 RSA content types must be replicated on any env switch, migration script, >200-char brand name bug
- [ABF permissions, JWT & DB map](abf-permissions-jwt-and-db-map.md) — perms live only in the JWT (SignalR + refreshtoken both dead); AspireProdBackup on port 3374 = UAT; roleclaims has XC 0/1 row pairs
- [ABE-5320 Porsche dealer sync](abe-5320-porsche-dealer-sync.md) — verified client-id map (Honda 38→380, Benz 68→338), the two-brand sync gate, 4 pre-existing gaps, DB tunnels, Playwright suite
- [ABE brand management](abe-brand-management.md) — 255-char brand split (item name 200 cap vs element), hide Delete when in use, JobInfo.brand widened on UAT, prod SQL pending
- [Release 28 Aug 2026](release-28aug-2026.md) — ABMB prod deployed 27 Aug 00:59; ABVB/ABF/ABCB deploys pending, dealer sweep, rsa-production hostname mystery
- [RSA Benefit redemption stranding](rsa-benefit-redemption-stranding.md) — 31 Aug incident: 504 strands a redemption, retries hit RoadSideJobId_UNIQUE; manual unblock + the endpoint still unfixed
- [ABE-5368 Porsche XLSX job report](abe-5368-porsche-xlsx-report.md) — 3 hard blockers (no Benefit API, no PTH field codes, tier mismatch), PTH ids per env, job→customer link path
- [ABE-5457 provider mobile flag](abe-5457-provider-mobile-flag.md) — Ver2 sync never writes isProviderMobile; Auto-mode autocomplete hides 317 prod providers; access recipe
- [ISOS Confluence write via twg](isos-confluence-write-via-twg.md) — Atlassian MCP is read-only/no folders on ISOS; twg CLI publishes; AD space 64782337, AI folder 6837207196, workflow-series page ids
