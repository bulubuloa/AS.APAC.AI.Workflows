# 08 — Complications to analyse before committing

Ten questions that decide whether the plan in `07` is right. Each has the facts as found, why it is hard, the options, and the decision it needs. They are cheaper to answer now than after the build.

---

## 1. Three copies, two candidates for "master"

**Facts.** A vendor exists in the Benefit portal's own database, in the CMS, and in Roadside. The portal writes to the first two. Some fields exist only in one place: the mobile flag only on the CMS roadside module (the portal's own `IsMobileVendorRSA` column is never set by the current vendor flow); the Benefit vendor ID only in the portal's database.

**Why it is hard.** "The CMS is the master for Roadside" does not settle what the *portal* treats as master. If the portal keeps a field the CMS does not have, the webhook path cannot carry it; if the CMS has a field the portal's database does not, the portal's own screens may disagree with Roadside.

**Options.** (a) CMS is master for everything vendor-related; the portal's vendor table becomes a cache too. (b) CMS is master for Roadside only; the portal guarantees the CMS is complete and keeps pushing the Benefit vendor ID. (c) Add the Benefit vendor ID to the CMS.

**Decide.** Which of (a)/(b)/(c). This is a Benefit-side ownership decision, not a Roadside one.

---

## 2. Identity, re-linking and duplicates

**Facts.** Roadside identifies a provider by `2-0938`; the CMS by an item ID; the two are linked by the CMS ID stored on the Roadside record. Roadside already has "(Duplicate)" rows and `tesst1` rows. A vendor recreated in the CMS (new item, same company) would arrive as a *new* provider: new ID, no vehicles, no login, no history.

**Why it is hard.** The mirror can only match on the CMS ID. Nothing today can say "this new CMS item is the same company as provider 2-0938".

**Options.** (a) Forbid recreating vendors; edits only. (b) Provide a controlled re-link tool (admin sets the CMS ID on an existing provider, mirror re-syncs). (c) Match by name as a fallback — the very thing the earlier Benefit fix removed.

**Decide.** (b), and who is allowed to use it.

---

## 3. "Published" is not "active"

**Facts.** The CMS read API returns published items only. Editors save drafts, schedule publishes, unpublish for housekeeping. Roadside's Active flag is an operational state ("may this provider be dispatched right now"). Today the detail page overlays CMS status `active` onto the Roadside flag; nothing maps *unpublished* to anything.

**Why it is hard.** A content workflow has more states than an on/off flag, and editors do not think of "unpublish" as "stop dispatching".

**Options.** (a) Unpublished / archived → Active = 0, published + status active → Active = 1, published + status inactive → Active = 0; record never deleted. (b) Treat unpublished as "no change" and rely on status only — but then an unpublished vendor is invisible to CMS reads yet active in Roadside. (c) Require editors to set status inactive before unpublishing, enforced by a CMS-side warning.

**Decide.** The mapping table, and whether editors get a warning when unpublishing a vendor with open jobs or ready vehicles.

---

## 4. Timing and eventual consistency

**Facts.** Kontent webhooks arrive seconds after publish, can arrive twice or out of order, and are retried on failure. The read API serves cached content for a short time after a change unless a "wait for fresh content" header is sent — which makes each call slower (1.0–1.6 s vs 0.2–0.45 s measured).

**Why it is hard.** For a few seconds an agent can see the old name on one screen and the new on the next; a webhook that arrives before the read API has the new content can mirror stale data.

**Options.** (a) Accept a delay of up to ~1 minute; mirror pulls with the fresh-content header; reconcile fixes anything that slips. (b) Demand zero delay — only possible by reading the CMS live everywhere, i.e. the slow design this audit rejects.

**Decide.** The acceptable delay between a CMS change and Roadside reflecting it. Everything about cache TTL and webhook handling follows from this number.

---

## 5. Deleting a vendor that has history

**Facts.** 51,764 jobs in the last year, each storing the provider ID and the name at save time. Vehicles, logins, grades and payments hang off the provider ID.

**Why it is hard.** A CMS delete is instant and total; Roadside history is permanent.

**Options.** (a) Never physically delete a Roadside provider that has any dependent row; CMS delete → Active = 0 + review flag. (b) Cascade delete — unacceptable.

**Decide.** (a), and confirm that the name stamped on each job is never overwritten (reports need it for vendors that no longer exist anywhere).

---

## 6. The roadside filter is a text match

**Facts.** Roadside decides who is a roadside provider by checking that category text contains "Auto Services" and sub-category text contains "Roadside Assistance". 24 active providers fail this today, including five towing companies filed under "Towing Assistance".

**Why it is hard.** Category is descriptive content that editors may reasonably change; "can be dispatched" is an operational fact.

**Options.** (a) Explicit yes/no flag on the roadside module (`07`, change 8). (b) Widen the text match to all "Auto Services" — still fragile. (c) Leave as is and re-file the 24 — fixes today, not tomorrow.

**Decide.** (a), before the switch; who sets it for the existing 752.

---

## 7. Data-quality baseline

**Facts.** 317 mobile-flag mismatches; 687 of 752 CMS vendors flagged mobile including BMW / Toyota / Nissan call centres, Benz Star Assist and International SOS Thailand; 24 misfiled; 7 unlinked; duplicates and test rows in Roadside; one CMS-linked provider whose CMS item is unpublished.

**Why it is hard.** The day the CMS becomes master, every one of these becomes live operational data with no Roadside copy to compare against.

**Options.** Clean in the CMS first (recommended), or accept and clean after (agents will see call centres in Auto mode).

**Decide.** Who cleans, against which rules, and the "clean enough to switch" threshold (e.g. drift report = 0 for 7 consecutive days).

---

## 8. Load and limits on the CMS

**Facts.** A full list is 1 call / 2.2 MB / 2.4–4.3 s; per-vendor 0.2–1.6 s; batch of 50 IDs ≈ 0.9 s. Today the search box downloads the full list per keystroke and the map calls the CMS once per vehicle. Kontent applies request limits per project and answers HTTP 429 when exceeded; the exact limit is not contractual.

**Why it is hard.** Moving more screens to the CMS without a cache multiplies calls; throttling shows up as random blanks, not as a clear failure.

**Options.** Cache (`07`, change 10) as a prerequisite; never per-row calls; batch by ID where per-item data is needed.

**Decide.** Confirm the cache is in scope before any screen moves; agree the CMS plan's request allowance with the vendor.

---

## 9. Environments share content

**Facts.** SIT and UAT read one shared CMS environment; SIT and pre-prod default to *production* CMS when unset; pre-prod points at production deliberately. Four Roadside-specific content types exist only in the environments they were hand-created in.

**Why it is hard.** With CMS as master and webhooks in play, a test edit in the wrong environment can rewrite production provider records, and a production publish can fire into a test Roadside.

**Options.** One CMS environment per Roadside environment, explicit config, webhook secrets per pair, content types replicated.

**Decide.** Environment matrix and who owns Kontent environment creation and cost.

---

## 10. What "no fallback" actually costs

**Facts.** Every CMS read in Roadside today is wrapped in "on failure, use the Roadside value". Removing it means a slow or failing CMS = empty search box, blank names on job pages and the customer link, empty provider lists, blank report columns, and dispatch stops.

**Why it is hard.** "No fallback" sounds like purity; operationally it means Roadside's availability becomes the CMS's availability, and the CMS is a third-party SaaS with its own maintenance windows.

**Options.** (a) Keep the mirror as fallback: users cannot tell the difference on a good day, and dispatch survives a bad one. (b) Cache-as-fallback with a visible staleness banner. (c) True no-fallback with clear error pages.

**Decide.** Whether dispatch may stop during a CMS incident. If the answer is no, "CMS only" describes the *editing* model (one writer) and not the *reading* model — which is the recommendation of this audit.

---

## Decision register

| # | Decision | Owner (suggested) | Blocks |
|---|---|---|---|
| 1 | Which store is master for the Benefit portal; how the Benefit vendor ID reaches Roadside | Benefit product owner | change 4 |
| 2 | Re-link rule and tool | Roadside + Benefit | change 3 |
| 3 | Published / unpublished / archived → Active mapping; editor warning | Business + CMS editors | change 5 |
| 4 | Acceptable CMS → Roadside delay | Operations | changes 3, 10 |
| 5 | Never delete providers with history; stamped names immutable | Roadside | change 5 |
| 6 | Explicit roadside flag; who sets it | CMS editors | change 8 |
| 7 | Clean-up rules and "clean enough" threshold | Business | change 9, 14 |
| 8 | Cache in scope; CMS request allowance | Engineering + vendor | change 10 |
| 9 | Environment matrix and Kontent cost | Engineering + finance | change 13 |
| 10 | May dispatch stop during a CMS incident? | Operations director | change 11 |
