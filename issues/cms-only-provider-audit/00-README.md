# Provider data from the CMS only — impact audit

**Premise under review:** the Roadside system (RSA) stops using its own copy of vendor / provider data and reads the CMS (Kontent) only, with no fallback to the Roadside database.

**What this set of documents does:** goes through every feature that touches provider data, explains how it works today, what it would take to run it on CMS data alone, what that costs in speed, reliability and behaviour, and what the pros and cons of each option are. Written so that a non-technical reader can follow the argument; the numbers behind every claim are in `10-numbers-and-evidence.md`.

Audit date: 16 Sep 2026. Production data and production code (`roadside-release-production`) were used throughout. Every database check was a read-only query.

## How to read this

**In a hurry?** Read [00a-manager-summary.md](00a-manager-summary.md): every feature, its verdict and the exact conditions, on one page. Each per-feature document also opens with a "Quick view for managers" box.

| File | Covers | Verdict at a glance |
|---|---|---|
| [01-dispatch-auto-mode.md](01-dispatch-auto-mode.md) | Provider search box, nearest-technician search, saving the job, Honda / Mercedes benefit check | 2 must stay on Roadside · 2 can move with conditions |
| [02-job-screens.md](02-job-screens.md) | Job detail page, live monitor board, job action list, customer tracking link, map markers | 1 must stay · 4 can move with conditions |
| [03-provider-management.md](03-provider-management.md) | Provider list, provider detail, provider review and grades, vehicle screens, direct edit | 1 must stay · 2 can move · 1 already on CMS · 1 must be closed |
| [04-provider-mobile-app.md](04-provider-mobile-app.md) | Login, lock-out of deactivated providers, vehicles / GPS / job updates | 2 must stay · 1 unaffected |
| [05-reports.md](05-reports.md) | Job Report, Complete Report, Compass Report, Job Detail export, Porsche XLSX, Provider Review — **with the volume analysis** | 0 must stay · all can move, but only one way |
| [06-background-and-sync.md](06-background-and-sync.md) | Lost-signal alerts, the Benefit → Roadside sync (v1 and v2), delete flows, environments | 2 must stay · 1 fix first |
| [07-architecture-changes.md](07-architecture-changes.md) | The 14 changes a CMS-master design needs, each with pros, cons, effort and risk | — |
| [08-complications.md](08-complications.md) | The 10 questions to settle before committing, with the decision each needs | — |
| [09-rollout-plan.md](09-rollout-plan.md) | Phased plan, success criteria per phase, rollback | — |
| [10-numbers-and-evidence.md](10-numbers-and-evidence.md) | Measurements, counts, queries, code references | — |

## Per-feature documents (one file each: today → CMS-only → CMS-master, with diagrams, load arithmetic, pros/cons)

| # | Feature | Verdict |
|---|---|---|
| [F01](features/F01-provider-search-box.md) | Provider search box on the job form | Can move, with conditions |
| [F02](features/F02-nearest-technicians.md) | Finding the nearest technicians (Auto-mode engine) | Must stay |
| [F03](features/F03-job-save-provider-name.md) | Saving the job with the chosen provider; hand-typed names | Can move, with conditions |
| [F04](features/F04-benefit-check.md) | Honda / Mercedes benefit check | Must stay |
| [F05](features/F05-job-detail-page.md) | Job detail page | Can move, with conditions |
| [F06](features/F06-live-monitor-board.md) | Live job monitor board | Must stay |
| [F07](features/F07-job-action-and-message-lists.md) | Job action list, message monitor | Can move, with conditions |
| [F08](features/F08-customer-tracking-link.md) | Customer tracking link | Can move, with conditions |
| [F09](features/F09-map-markers.md) | Map markers (all vehicles) | Can move, with conditions |
| [F10](features/F10-provider-list.md) | Provider list | Can move, with conditions |
| [F11](features/F11-provider-detail-page.md) | Provider detail page | Already on the CMS |
| [F12](features/F12-provider-review-and-grades.md) | Provider review and grades | Must stay |
| [F13](features/F13-vehicle-health-and-summary.md) | Vehicle health / summary screens | Already on the CMS |
| [F14](features/F14-direct-provider-edit.md) | Direct provider edit in Roadside | Must be closed |
| [F15](features/F15-provider-login.md) | Provider login | Must stay |
| [F16](features/F16-lockout-deactivated-provider.md) | Lock-out of deactivated providers | Must stay |
| [F17](features/F17-app-vehicles-gps-jobs.md) | App: vehicles, GPS, job updates | Unaffected |
| [F18](features/F18-job-reports.md) | Job / Complete / Compass / Porsche reports | Can move (mirror) |
| [F19](features/F19-job-detail-export.md) | Job Detail export | Can move, with conditions |
| [F20](features/F20-lost-signal-alerts.md) | Lost-signal alerts | Must stay |
| [F21](features/F21-benefit-to-roadside-sync.md) | Benefit → Roadside sync → the Mirror | Must keep and fix |
| [F22](features/F22-delete-and-unpublish.md) | Delete / unpublish / archive | Decision needed |
| [F23](features/F23-environments.md) | Environments | Fix first |

## The one-paragraph answer

"CMS only, no fallback" is not achievable as stated: seven features need a provider record inside the Roadside database (logins, the per-request active check, the nearest-technician search, the Honda / Mercedes benefit ID, grades, the live monitor board, lost-signal alerts), and every job, vehicle and payment is tied to a Roadside provider ID that the CMS cannot create. What *is* achievable, and gives users the same result, is **CMS as the master, Roadside as an always-complete mirror**: the CMS is the only place a vendor is edited; a CMS webhook keeps the Roadside copy complete and fresh; screens read the mirror (fast, works offline from the CMS) and the CMS through a cache where up-to-the-second data matters. The drift that started this discussion — 317 providers hidden from Auto mode because the sync never copies the "mobile" flag — is fixed by the same mirror.

## Glossary

| Term | Meaning in these documents |
|---|---|
| **Roadside / RSA** | The dispatch system agents use (GAN screens, the dispatch engine, the provider mobile app backend). Has its own database. |
| **Provider record** | A row in the Roadside database for one vendor: ID like `2-0938`, login, display name, Active flag, Mobile Provider flag, group, phone, email, note, CMS link. |
| **CMS** | Kontent. Where the Benefit team manages vendors. A vendor is a "template_generic" item plus a "roadside module" holding the roadside-specific fields (RSA username, mobile vendor yes/no). |
| **Benefit portal** | The vendor-management web app (ABF front end, ABVB back end). Writes to its own database and to the CMS, and pushes a copy of each vendor to Roadside. |
| **Sync / push** | The call the Benefit portal makes to Roadside when a vendor is saved. Two versions exist (v1 and v2); v2 is the live one and copies fewer fields. |
| **Overlay** | Where a Roadside screen reads its own record and then replaces some fields with live CMS values. Introduced in 2026. |
| **Auto mode** | A job where the system finds the nearest available technician vehicle by GPS. Only "mobile" providers take part. |
| **Manual mode** | A job where the agent picks the provider by name. Any active provider can be chosen. |
| **Mirror** | The proposed design: Roadside keeps a complete, automatically refreshed copy of every CMS vendor field, but never edits it. |

## Production baseline (16 Sep 2026)

| Measure | Value |
|---|---|
| Active providers in Roadside | 719 (712 linked to a CMS vendor, 7 not) |
| Jobs, last 90 days | 13,622 — 8,338 Auto (82 providers used) / 5,284 Manual (356 providers used) |
| Jobs, last 365 days | 51,764 — 51,761 on providers that resolve in the CMS |
| Vehicles | 1,038 across 414 providers |
| CMS roadside vendors | 752 (687 flagged mobile, 651 active + mobile) |
| Providers hidden from Auto mode by the mobile-flag drift | 317 |
| Active providers the CMS search cannot see | 24 (filed outside "Roadside Assistance") + 7 (no CMS record) |
| One full CMS vendor list | 1 request, ~2.2 MB, 2.4 – 4.3 s; no cache anywhere |
| One CMS vendor by ID | 1.0 – 1.6 s (with the "wait for fresh content" header the code always sends); 0.2 – 0.45 s without |

## Severity scale used throughout

- **Must stay on Roadside** — the CMS does not hold what the feature needs, or the feature runs where a CMS call is impossible (inside a database query, a background timer, a real-time push).
- **Can move, with conditions** — the feature only needs provider *details* and can read them from the CMS, once a named prerequisite is met.
- **Already on the CMS / unaffected** — no visible change.
