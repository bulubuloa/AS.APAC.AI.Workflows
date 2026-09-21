# Manager summary — every feature, its verdict, and the conditions

One page for readers who will not open the per-feature documents. Each row links to the full analysis.

**The short answer:** "CMS only, no fallback" is not achievable — 7 features need a provider record inside Roadside. "CMS as the master, Roadside as an always-fresh copy" gives users the same result and needs the conditions below. Fixing the sync (F21) is the first step and is already in progress.

## Bottom line — what stays in Roadside, what lives in the CMS

**Rule:** Roadside keeps only what dispatch and the technician app need to operate; everything descriptive about a vendor is edited in the CMS and only *copied* into Roadside by the sync.

| Stays in Roadside | Why |
|---|---|
| Provider ID (`2-0938`) | every vehicle, job, photo and payment hangs off it; the CMS cannot create it |
| Login + password | technicians sign in against it; a CMS must never hold credentials |
| **Active** flag — read-only copy of CMS status | checked on every app request and inside the nearest-technician query |
| **Mobile** flag — read-only copy of CMS "mobile vendor" | the Auto-mode gate |
| Vehicles, GPS, ready / on-job state, push tokens, service types | the dispatch engine itself |
| Grades, job history, KPI | Roadside-only concepts |
| Benefit vendor ID | Honda / Mercedes benefit check |
| CMS item ID | the link to the vendor's CMS record |
| Display name — read-only copy of the CMS name | the live board, the customer link and reports read it inside SQL |

| Lives in the CMS only | |
|---|---|
| Vendor name, status, group, country, phone, email, note, category, contract text | everything a person edits — never edited in Roadside |

The three "read-only copy" rows are the whole point: Active, Mobile and the name are **owned** by the CMS but must also **exist** in Roadside, because the flows that use them are database queries and per-request checks that cannot call the CMS. Only the sync may write those copies (direct edit in Roadside is closed).

## Can move, with conditions

### [F01 — Provider search box on the job form](features/F01-provider-search-box.md)  
**Can move, with conditions.** Conditions:
1. The Roadside copy carries the CMS mobile flag (the sync must write it — the ABE-5457 fix does this; then the one-off backfill of 317 providers).
2. The BA confirms who is really "mobile" in the CMS: 687 of 752 vendors are flagged mobile today, including call centres such as BMW / Toyota / Nissan Call Center.
3. The 24 vendors filed outside "Roadside Assistance" and the 7 with no CMS record are cleaned up in the CMS, or they disappear from the search box.
4. Search keeps matching on Roadside login as well as CMS name (agents type both).
5. If the CMS is read directly per keystroke: a cache first — a full CMS list takes 2–4 s and the box asks on every character.

*What we get:* Every mobile provider appears in Auto-mode search; one spelling of every name; search stays instant.

### [F03 — Saving the job with the chosen provider](features/F03-job-save-provider-name.md)  
**Can move, with conditions.** Conditions:
1. The provider name stamped on a job must never be blank — so on a CMS error the Roadside name (or the mirror) is used, never an empty value.
2. Hand-typed provider names on Honda / Mercedes benefit jobs must match the CMS spelling — or the option to type a name is removed now that the search box offers every vendor.
3. The provider record must still exist in Roadside: the job stores the Roadside ID.

*What we get:* Job records carry the CMS name from the moment of save; no extra CMS call per save if the mirror is used.

### [F05 — Job detail page](features/F05-job-detail-page.md)  
**Can move, with conditions.** Conditions:
1. A rule for unpublished / draft vendors — the page must show the last known name, not a blank, when a vendor is taken down mid-job.
2. Read the name from the Roadside copy (0 CMS calls) or through a cache; not a 1–1.5 s CMS call on every open of the busiest page.
3. On CMS failure the page still shows a provider name.

*What we get:* Job page opens ~1 s faster than today; name always equals the CMS name.

### [F07 — Job action list, message monitor](features/F07-job-action-and-message-lists.md)  
**Can move, with conditions.** Conditions:
1. Names read from the Roadside copy or a cache — never one CMS call per row (a 200-row page would take minutes).

*What we get:* No visible change; names equal the CMS name.

### [F08 — Customer tracking link](features/F08-customer-tracking-link.md)  
**Can move, with conditions.** Conditions:
1. Name read from the Roadside copy — this is a public page customers reload while waiting at the roadside; it must not depend on a third-party API or show a blank company name.

*What we get:* Customer sees the CMS spelling of the provider; page stays instant.

### [F09 — Map markers (all vehicles)](features/F09-map-markers.md)  
**Can move, with conditions.** Conditions:
1. A cache for the vendor list (the map already downloads it on every load).
2. Vehicle details fetched in batches of 50 or mirrored into Roadside — today it is one CMS call per vehicle, hundreds per map load.
3. Group-icon rule keeps handling both spellings ("Honda" / "Honda RSA").

*What we get:* Map loads in seconds instead of minutes of CMS time; pins never go blank.

### [F10 — Provider list](features/F10-provider-list.md)  
**Can move, with conditions.** Conditions:
1. The Roadside copy is complete: the sync writes every CMS field (name, status, group, mobile, country, email) so the list shows CMS values without a 2–4 s CMS download per page.
2. The 31 providers the CMS does not recognise are resolved in the CMS (24 filed outside "Roadside Assistance", 7 with no CMS record) — otherwise they vanish from the list, which already happened once and was reverted.
3. Search still works on Roadside ID and login, not only CMS vendor name.
4. A rule for unpublished / draft vendors: shown as inactive, not missing.

*What we get:* The list shows exactly what the Benefit team edited, instantly, with no missing providers.

### [F18 — Job / Complete / Compass / Porsche reports](features/F18-job-reports.md)  
**Can move — one way only.** Conditions:
1. Never call the CMS per report row: a 3-month report is ~13,000 rows, which would take 3.5–6 hours and be throttled. One list call per run, a batched lookup by provider, or the Roadside copy are the only workable designs.
2. Keep the name stamped on each job as the last fallback, so vendors that are later unpublished or deleted still have a name on historical rows.
3. Decide whether a CMS outage may produce a report with a blank vendor column (today it falls back to Roadside names).

*What we get:* All four reports print the same CMS name (today the Complete and Compass reports disagree with the Job Report after a rename).

### [F19 — Job Detail export](features/F19-job-detail-export.md)  
**Can move, with conditions.** Conditions:
1. One CMS call per export at most, cached — this export is sometimes run in a loop over hundreds of jobs, which becomes the per-row case.
2. Preferably read the name from the Roadside copy (0 calls).

*What we get:* No visible change.

## Must stay on Roadside (the CMS cannot supply what these need)

- **[F02 — Finding the nearest technicians (Auto mode)](features/F02-nearest-technicians.md)** — The nearest-technician search is one database query over vehicles, GPS positions, service types, provider grade and distance — none of which exist in the CMS. The only CMS-owned input is the provider's Active flag, and the sync keeps that correct. Nothing to move; nothing lost.
- **[F04 — Honda / Mercedes benefit check](features/F04-benefit-check.md)** — The Benefit system checks the provider by a Benefit vendor ID stored on the Roadside record (an earlier fix replaced fragile name matching). That ID is not in the CMS. Either it keeps arriving from the Benefit portal, or the CMS content model is extended to carry it — a Benefit-side decision.
- **[F06 — Live job monitor board](features/F06-live-monitor-board.md)** — The board re-renders on every job event and is pushed live to every screen. Names must come from the database the render already reads; a CMS call per event would put the board minutes behind and gigabytes per hour on the CMS. The sync keeps the stored name equal to the CMS name.
- **[F12 — Provider review and grades](features/F12-provider-review-and-grades.md)** — Grades are a Roadside concept stored against the Roadside ID; the CMS has no grades and the per-grade summary is a database count. Only the name search could use CMS data.
- **[F15 — Provider login](features/F15-provider-login.md)** — Usernames, password hashes and login tokens live in Roadside. A content system cannot and must not hold credentials. Every provider keeps a Roadside record for as long as anyone from that provider can sign in.
- **[F16 — Lock-out of deactivated providers](features/F16-lockout-deactivated-provider.md)** — Every request from the technician app checks the provider's Active flag in Roadside — thousands of times an hour. Asking the CMS each time is not workable. The sync must copy CMS status into that flag; then deactivating a vendor in the CMS locks its technicians out within seconds. If this is forgotten, deactivating in the CMS does not stop the technicians.
- **[F20 — Lost-signal alerts](features/F20-lost-signal-alerts.md)** — A background timer checks vehicles of active providers for lost GPS every few minutes. It runs inside the database with no web request and cannot cheaply ask the CMS per tick. The sync keeps the Active flag correct.

## Already on the CMS / unaffected

- **[F11 — Provider detail page](features/F11-provider-detail-page.md)** — This page already reads the CMS live for every field. Nothing to do; it is the preview of what the rest of the system would look like.
- **[F13 — Vehicle health / summary screens](features/F13-vehicle-health-and-summary.md)** — These screens already show only providers the CMS returns (which is why the 31 unrecognised vendors are already missing here). A cache removes the 2–4 s per view.
- **[F17 — App: vehicles, GPS, job updates](features/F17-app-vehicles-gps-jobs.md)** — Vehicles, GPS and job updates are tied to the provider's Roadside ID and never read provider details. No change — as long as the Roadside record exists.

## Must be done before any switch

- **[F21 — Benefit → Roadside sync](features/F21-benefit-to-roadside-sync.md)** — *Must keep running — and be fixed first.* The sync is the only thing that creates a Roadside provider record, and seven features need that record. "CMS only" does not remove it; it changes its job from "copy some fields when the portal saves" to "keep a complete mirror whenever the CMS changes" (webhook + nightly reconcile). Today it drops the mobile flag, country and email — the cause of the 317 hidden providers.
- **[F14 — Direct provider edit in Roadside](features/F14-direct-provider-edit.md)** — *Must be closed.* The Roadside save API still lets an admin change a provider's name, contact or Active flag. With the CMS as master this path must be switched off for providers (kept for staff accounts and password reset), or the two systems drift apart again. An emergency-fix path, if wanted, must write to the CMS.
- **[F22 — Delete / unpublish / archive](features/F22-delete-and-unpublish.md)** — *Decision needed.* What should Roadside do when a vendor is unpublished, archived or deleted in the CMS? Recommended: set inactive, keep the record and its history, never delete. Without this rule, an unpublished vendor becomes invisible to agents while its technicians keep receiving jobs.
- **[F23 — Environments](features/F23-environments.md)** — *Fix first.* SIT and pre-prod currently read the production CMS by default, and SIT/UAT share one CMS environment. Before the CMS becomes master, each Roadside environment needs its own CMS environment and its own webhook, or test edits can reach production data.

## The conditions, de-duplicated (what the programme actually has to deliver)

| # | Condition | Unblocks |
|---|---|---|
| 1 | Sync copies **every** CMS field (mobile flag, country, email today; then status/name/group on every CMS change via webhook + nightly reconcile) | F01, F03, F05, F06, F07, F08, F10, F16, F18, F19, F20 |
| 2 | BA confirms the CMS **mobile flag** (687 of 752 vendors flagged, incl. call centres) and the backfill of 317 providers runs | F01, F02 |
| 3 | The **31 vendors** the CMS does not recognise are cleaned up (24 mis-filed, 7 unlinked) and an explicit "roadside provider" flag replaces the category-text test | F01, F10, F13 |
| 4 | Rule for **unpublished / archived / deleted** vendors (inactive, never deleted; history kept) | F05, F10, F18, F22 |
| 5 | **Search** keeps matching Roadside ID and login, not only CMS name | F01, F03, F10 |
| 6 | A **cache** for any screen that reads the CMS directly; never one CMS call per row or per keystroke | F01, F09, F13, F18, F19 |
| 7 | **Outage behaviour** decided: Roadside copy as fallback (recommended) or explicit errors — never silent blanks | F01, F03, F05, F08, F18 |
| 8 | Direct provider edit in Roadside **closed**; old v1 push retired | F14, F21 |
| 9 | One CMS environment per Roadside environment | F23 |
| 10 | Benefit vendor ID keeps reaching Roadside (portal push, or added to the CMS) | F04 |
